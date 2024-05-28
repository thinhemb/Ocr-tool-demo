import cv2
import numpy as np
from PIL import Image

from pipeline.data_obj.ann import TextAnn

from pipeline.base_obj import BaseDetector
from app.Ocr.det import TextDetector


class PaddleTextDetection(BaseDetector):
    def __init__(self, config):
        self.config = config

        self.text_detector = TextDetector(path_model=self.config["det"])

    def predict(self, image):
        # new_image = image.copy()
        new_image = self.alpha_to_color(image)
        result = self.text_detector(image=new_image)
        img_crop_list = []
        if result is not None:
            new_image = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
            for r in range(len(result)):
                coord = [i for sub in result[r] for i in sub]
                ocr_line = self.convert_to_ocr_line(coord, new_image)
                img_crop_list.append(ocr_line)
        return img_crop_list

    @staticmethod
    def alpha_to_color(image, alpha_color=(255, 255, 255)):
        if len(image.shape) == 3 and image.shape[2] == 4:
            b, g, r, a = cv2.split(image)
            alpha = a / 255

            r = (alpha_color[0] * (1 - alpha) + r * alpha).astype(np.uint8)
            g = (alpha_color[1] * (1 - alpha) + g * alpha).astype(np.uint8)
            b = (alpha_color[2] * (1 - alpha) + b * alpha).astype(np.uint8)

            image = cv2.merge((b, g, r))
        return image

    @staticmethod
    def convert_to_ocr_line(coord, img, add_margin=0.2, model_height=64):
        h, w = img.shape[:2]
        x_min = int(min(coord[::2]))
        x_max = int(max(coord[::2]))
        y_min = int(min(coord[1::2]))
        y_max = int(max(coord[1::2]))

        margin = int(add_margin * (y_max - y_min))

        x_min = max(0, x_min - margin)
        x_max = min(w, x_max + margin)
        y_min = max(0, y_min - margin)
        y_max = min(h, y_max + margin)

        crop_img = img[y_min: y_max, x_min:x_max]

        ratio = (x_max - x_min) / (y_max - y_min)
        crop_img = cv2.resize(crop_img, (int(model_height * ratio), model_height),
                              interpolation=Image.LANCZOS)
        update_coord = [[x_min, y_min], [x_max, y_min], [x_max, y_max], [x_min, y_max]]
        return TextAnn.from_coord_and_img(update_coord, w, h, crop_img)
