from typing import Optional, List

import numpy as np

from pipeline.data_obj.datapoint import DataPoint
from pipeline.data_obj.ann import TextAnn
from pipeline.base_obj import PipelineComponent, BaseDetector

from pipeline.utils.text_utils import filter_result


class TextExtractionComponent(PipelineComponent):
    def __init__(self, d_text_predictor: BaseDetector, rec_predictor: BaseDetector):
        self.d_text_predictor = d_text_predictor
        self.rec_predictor = rec_predictor

    def predict_ocr(self, img_list: List[TextAnn], lang, prob_threshold=None) -> Optional[List[TextAnn]]:
        img_list = sorted(img_list, key=lambda x: x.top)
        for index, item in enumerate(img_list):
            img = item.get_img
            label, prob = self.rec_predictor.predict(img, lang)
            if label is None or label.strip() == '' or label.strip() == "U":
                item.label = '0'
                prob = 0.5
            else:
                item.label = label
            if prob_threshold is not None and prob < prob_threshold:
                continue

            item.prob = prob
        return [item for item in img_list if item.label is not None]

    def serve(self, dp: DataPoint) -> None:
        np_img = dp.image
        # Check if image is blank
        if np.mean(np_img) > 254.5:
            return

        prob_threshold = dp.analyze_config.ocr_prob_threshold
        height_threshold = dp.analyze_config.ocr_height_threshold

        list_img = self.d_text_predictor.predict(np_img)

        list_text = self.predict_ocr(list_img, dp.lang, prob_threshold=prob_threshold)

        dp.text_anns = filter_result(list_text, height_threshold)

    def health_check(self) -> bool:
        return self.rec_predictor is not None
