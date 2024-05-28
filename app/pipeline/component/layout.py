from typing import List

from pipeline.base_obj import BaseDetector, ForkComponent
from pipeline.data_obj.datapoint import DataPoint


class RegionDetectComponent(ForkComponent):
    def __init__(self, predictor: BaseDetector):
        self.predictor = predictor

    def serve(self, dp: DataPoint) -> List[DataPoint]:
        type_, crop_image = self.predictor.predict(dp.image)

        dps = []
        # for crop_image in crop_images:
        new_dp = dp.clone()
        new_dp.type_image = type_
        new_dp.image = crop_image
        new_dp.width = crop_image.shape[1]
        new_dp.height = crop_image.shape[0]
        dps.append(new_dp)
        return dps

    def health_check(self) -> bool:
        return self.predictor is not None
