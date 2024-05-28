
from pipeline.base_obj import BaseDetector
# from pipeline.data_obj.ann import TextAnn
# from common_utils.img_utils import four_point_transform
from app.Ocr.rec import TextRecognizer


class RecognitionOCR(BaseDetector):
    def __init__(self, config):
        # self.config = Config("ocr")
        self.config = config
        # print(self.config)
        self.text_recognizer = TextRecognizer(self.config["rec_en"], self.config["rec_japan"])

    def predict(self, image, lang):
        result = self.text_recognizer([image], lang)
        if result[0]:
            label = result[0][0]
            prob = result[0][1]
            return label, prob
