import numpy as np
import onnxruntime

from app.Ocr.utils import OperatorGroup
from .preprocess import Resize, Normalize, HWCToCHW, PickKeys
from .postprocess import DBPostProcess


class TextDetector:
    def __init__(self, path_model, box_thresh=0.5, unclip_ratio=0.7):
        self.box_thresh = box_thresh
        self.unclip_ratio = unclip_ratio
        self.path_model = path_model

        self.preprocess_op = OperatorGroup(
            Resize(limit_side_len=640),
            Normalize(std=[0.229, 0.224, 0.225], mean=[0.485, 0.456, 0.406]),
            HWCToCHW(),
            PickKeys('image', 'shape')
        )
        self.post_process_op = DBPostProcess(thresh=0.6)
        self.output_tensors = None
        self.predictor = self.load_model()
        self.input_tensor = self.predictor.get_inputs()[0]

    def load_model(self):
        so = onnxruntime.SessionOptions()
        so.log_severity_level = 3
        session = onnxruntime.InferenceSession(self.path_model, so, providers=onnxruntime.get_available_providers())
        return session

    @staticmethod
    def order_points_clockwise(pts):
        """
        reference from: https://github.com/jrosebr1/imutils/blob/master/imutils/perspective.py
        # sort the points based on their x-coordinates
        """
        xsorted = pts[np.argsort(pts[:, 0]), :]

        # grab the left-most and right-most points from the sorted
        # x-roodinate points
        leftmost = xsorted[:2, :]
        rightmost = xsorted[2:, :]

        # now, sort the left-most coordinates according to their
        # y-coordinates, so we can grab the top-left and bottom-left
        # points, respectively
        leftmost = leftmost[np.argsort(leftmost[:, 1]), :]
        (tl, bl) = leftmost

        rightmost = rightmost[np.argsort(rightmost[:, 1]), :]
        (tr, br) = rightmost

        rect = np.array([tl, tr, br, bl], dtype=np.float32)
        return rect

    @staticmethod
    def clip_det_res(points, img_height, img_width):
        for pno in range(points.shape[0]):
            points[pno, 0] = int(min(max(points[pno, 0], 0), img_width - 1))
            points[pno, 1] = int(min(max(points[pno, 1], 0), img_height - 1))
        return points

    def filter_tag_det_res(self, dt_boxes, image_shape):
        img_height, img_width = image_shape[0:2]
        dt_boxes_new = []
        for box in dt_boxes:
            box = self.order_points_clockwise(box)
            box = self.clip_det_res(box, img_height, img_width)
            if np.linalg.norm(box[0] - box[1]) < 4 or np.linalg.norm(box[0] - box[3]) < 4:
                continue
            dt_boxes_new.append(box)
        return np.array(dt_boxes_new)

    def __call__(self, image):

        img, shape = self.preprocess_op(image)

        input_dict = {self.input_tensor.name: img[None]}

        outputs = self.predictor.run(self.output_tensors, input_dict)

        post_result = self.post_process_op(outputs[0], shape[None], self.unclip_ratio, self.box_thresh)
        dt_boxes = post_result[0]
        dt_boxes = self.filter_tag_det_res(dt_boxes, shape[:2])

        return dt_boxes
