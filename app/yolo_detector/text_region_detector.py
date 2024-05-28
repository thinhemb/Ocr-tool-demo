import os
import time

import onnxruntime
from yolo_detector.yolo import YOLO

from pipeline.base_obj import BaseDetector
from object_models.exceptions import DetectException
from yolo_detector.corner_utils import results_to_dataframe, get_type, crop_img_without_corner, \
    horizontal_img_without_corner


class YoloRegionTextDetector(BaseDetector):
    def __init__(self, config):
        self.config = config
        self.yolo_model_path = self.choose_model_path()

        self.conf = self.config["confidence_threshold"]
        self.iou = self.config["iou_threshold"]

        self.model = self.load_model()

    def load_model(self):
        so = onnxruntime.SessionOptions()
        so.log_severity_level = 3
        session = onnxruntime.InferenceSession(self.yolo_model_path, so,
                                               providers=onnxruntime.get_available_providers())
        model = YOLO(session, self.conf, self.iou)
        return model

    def choose_model_path(self):
        yolo_model_path = os.path.join(self.config["model_dir"], "yolo", "best.onnx")
        return yolo_model_path

    def inference(self, img):
        # start = time.perf_counter()
        box, scores, class_names = self.model.predict(img)
        # print(f"Inference time detect zone: {(time.perf_counter() - start) * 1000:.2f} ms")
        df_result = None
        if len(box):
            df_result = results_to_dataframe(box, scores, class_names)
        return df_result

    def predict(self, img):
        # if self.num_torch_threads is not None:
        #     torch.set_num_threads(self.num_torch_threads)
        try:
            df_result = self.inference(img)
            df_type = get_type(df_result)
            if len(df_type['name'].values.tolist()) > 0:
                type_name = df_type['name'].values.tolist()[0]
                img_crop = crop_img_without_corner(df_type, img)
                img_crop = horizontal_img_without_corner(df_type, img_crop)
                return type_name, img_crop
            else:
                return "3", img[143:273, 1:959]

        except Exception as err:
            print(err)
            raise DetectException('model not detect region in image')
