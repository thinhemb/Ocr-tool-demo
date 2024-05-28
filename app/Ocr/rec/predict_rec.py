import math
import cv2
import numpy as np
import onnxruntime

from app.Ocr.utils import get_character_dict
from .rec_decoder import CTCLabelDecode


class TextRecognizer:
    def __init__(self, path_model_en, path_model_japan):
        self.rec_image_shape = [3, 48, 320]
        self.rec_batch_num = 4
        self.post_process_op_en = CTCLabelDecode(character_dict=get_character_dict('en'))
        self.post_process_op_japan = CTCLabelDecode(character_dict=get_character_dict('japan'))

        self.predictor_en = self.load_model(path_model_en)
        self.input_tensor_en = self.predictor_en.get_inputs()[0]

        self.predictor_japan = self.load_model(path_model_japan)
        self.input_tensor_japan = self.predictor_japan.get_inputs()[0]
        self.output_tensors = None

    @staticmethod
    def load_model(path_model):
        so = onnxruntime.SessionOptions()
        so.log_severity_level = 3
        model = onnxruntime.InferenceSession(path_model, so,
                                             providers=onnxruntime.get_available_providers())
        return model

    def resize_norm_img(self, img, max_wh_ratio):
        img_c, img_h, img_w = self.rec_image_shape

        img_w = int(img_h * max_wh_ratio)
        resized_w = min(img_w, int(math.ceil(img_h * img.shape[1] / img.shape[0])))

        resized_image = cv2.resize(img,
                                   (resized_w, img_h),
                                   interpolation=cv2.INTER_CUBIC
                                   ).astype('float32') / 255.
        # resized_image = resized_image.transpose((2, 0, 1)) / 255.
        resized_image -= 0.5
        resized_image /= 0.5
        padding_im = np.zeros((img_c, img_h, img_w), dtype=np.float32)
        padding_im[:, :, 0:resized_w] = resized_image
        return padding_im

    def __call__(self, img_list, lang):
        img_num = len(img_list)
        # Sorting can speed up the recognition process
        indices = np.argsort([img.shape[1] / img.shape[0] for img in img_list])

        rec_res = [['', 0.0]] * img_num
        batch_num = self.rec_batch_num
        for beg_img_no in range(0, img_num, batch_num):
            end_img_no = min(img_num, beg_img_no + batch_num)
            h, w = img_list[indices[end_img_no - 1]].shape[:2]
            norm_img_batch = np.concatenate([
                self.resize_norm_img(img_list[indices[ino]], w / h)[None]
                for ino in range(beg_img_no, end_img_no)
            ]).copy()
            if lang == 'en':
                input_dict = {self.input_tensor_en.name: norm_img_batch}
                rec_res = self.infer(self.predictor_en, self.post_process_op_en, rec_res, beg_img_no, indices,
                                     input_dict)
            elif lang == 'japan':
                input_dict = {self.input_tensor_japan.name: norm_img_batch}
                rec_res = self.infer(self.predictor_japan, self.post_process_op_japan, rec_res, beg_img_no, indices,
                                     input_dict)
        return rec_res

    def infer(self, model, post_process_op, rec_res, beg_img_no, indices, input_dict):

        outputs = model.run(self.output_tensors, input_dict)

        for rno, res in enumerate(post_process_op(outputs[0])):
            rec_res[indices[beg_img_no + rno]] = res
        return rec_res
