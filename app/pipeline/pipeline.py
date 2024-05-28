import time
import os
from dataclasses import dataclass
from typing import List

from pipeline.config.analyze_config import AnalyzeConfig
from mapper.mapper import TableMapper
import log
from pipeline.base_obj import BaseDetector, PipelineComponent, BasePipeline, PreProcessComponent, \
    PostProcessComponent, ForkComponent

from pipeline.component.layout import RegionDetectComponent
from pipeline.component.pre import LoadImageComponent
from pipeline.component.text_extract.text_default import TextExtractionComponent
from pipeline.config.key_value_config import KeyValueConfig
from yolo_detector.text_region_detector import YoloRegionTextDetector
from Ocr.pp_ocr_rec import RecognitionOCR
from Ocr.pp_ocr_det import PaddleTextDetection
from config.config import Config
from pipeline.component.text_order.order_key_value import KeyValueTextOrderComponent


# from object_models.result_obj import TableInfo


@dataclass
class ShareInfo:
    rotated: bool = None


class Pipeline(BasePipeline):
    def __init__(
            self,
            model_config,
            pre_component: PreProcessComponent,
            split_component: ForkComponent,
            pipeline_component_list: List[PipelineComponent],
            post_component: PostProcessComponent
    ):
        self.model_config = model_config
        self.pre_component = pre_component
        self.split_component = split_component
        self.pipeline_component_list = pipeline_component_list
        self.post_component = post_component

    @classmethod
    def build(cls, model_config, lang='japan',
              pre_component: PreProcessComponent = None,
              d_region_text: BaseDetector = None,
              d_text_predictor: BaseDetector = None,
              rec_predictor: BaseDetector = None,
              key_value_config: KeyValueConfig = None,
              mapper: PostProcessComponent = None,
              ):
        # model_config = cls.init_torch(model_config)

        if pre_component is None:
            pre_component = LoadImageComponent()

        model_config_yolo_det = Config("yolo_det").get_json()

        if d_region_text is None:
            try:
                d_region_text = YoloRegionTextDetector(model_config_yolo_det)
                log.dlog_i("Region text detector is loaded")
            except Exception as e:
                log.dlog_e("Region text detector is not loaded")
                raise e
        split_component = RegionDetectComponent(d_region_text)

        model_config_ocr = Config("ppocr").get_json()

        if d_text_predictor is None:
            try:
                d_text_predictor = PaddleTextDetection(model_config_ocr)
                log.dlog_i("d_text predictor is loaded")
            except Exception as e:
                log.dlog_e("d_text predictor is not loaded")
                raise e

        components = []

        if rec_predictor is None:
            try:
                rec_predictor = RecognitionOCR(model_config_ocr)
                log.dlog_i("Rec predictor is loaded")
            except Exception as e:
                log.dlog_e("Rec predictor is not loaded")
                raise e
        rec_text = TextExtractionComponent(d_text_predictor, rec_predictor)
        components.append(rec_text)

        if key_value_config is None:
            try:
                key_value_config = KeyValueConfig.from_json(
                    os.path.join("data", "envs", "table_config.json")
                )
                log.dlog_i("Key value config is loaded")
            except Exception as e:
                log.dlog_e("Key value config is not loaded")
                raise e

        order = KeyValueTextOrderComponent(
            key_value_config,
            same_key_top_tolerance=0.02,
            same_key_left_tolerance=0.02,
            left_right_key_tolerance=0.1
        )
        components.append(order)
        if mapper is None:
            mapper = TableMapper(lang)

        return cls(model_config, pre_component, split_component, components, mapper)

    def analyze(self, path, lang, analyze_config=None):
        if analyze_config is None:
            analyze_config = AnalyzeConfig()
        # result = None
        dp = self.pre_component.serve(path, analyze_config)
        dp.lang = lang
        dps = self.split_component.serve(dp)
        for dp in dps:
            c = ""
            try:
                for c in self.pipeline_component_list:
                    start_time = time.time()
                    c.serve(dp)
                    log.dlog_d(f'{c.__class__.__name__}. Processing for {time.time() - start_time:.2f}')
            except Exception as e:
                log.dlog_e(f'{c.__class__.__name__}. Error: {e}')
                continue
        result = self.post_component.serve(dps)
        return result
