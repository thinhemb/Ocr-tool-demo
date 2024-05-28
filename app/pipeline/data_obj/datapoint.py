import copy
from dataclasses import dataclass, field
from typing import Optional, List

import cv2
import numpy as np

from pipeline.config.analyze_config import AnalyzeConfig
from pipeline.data_obj.ann import TextAnn, LayoutAnn
from pipeline.utils.datatypes import ImageType


@dataclass
class DataPoint:
    file_name: str
    file_type: str
    lang: str
    location: str = field(default="")
    analyze_config: AnalyzeConfig = AnalyzeConfig()
    type_image: str = field(default=None)
    pdf_obj: dict = field(default_factory=dict)
    # For Excel and docx files that are converted to pdf
    original_file_path: str = field(default="", init=False, repr=False)

    image: Optional[ImageType] = field(default=None)
    width: int = field(default=0)
    height: int = field(default=0)
    text_anns: List[TextAnn] = field(default_factory=list, init=False, repr=False)
    layout_anns: List[LayoutAnn] = field(default_factory=list, init=False, repr=False)
    img_label: str = field(default=None)
    structured_data: Optional[object] = field(default=None, repr=False)
    meta: any = None

    def get_text(self, seperator: str = "\n", show_form_tag=False) -> str:
        if show_form_tag:
            return seperator.join([
                f"{ann.label} ---> {ann.form_tag}" if ann.form_tag else ann.label
                for ann in self.text_anns
            ])
        return seperator.join([ann.label for ann in self.text_anns])

    def to_json(self):
        return {
            "file_name": self.file_name,
            "location": self.location,
            "width": self.width,
            "height": self.height,
            "text_anns": [ann.to_json() for ann in self.text_anns],
        }

    def clone(self):
        return copy.deepcopy(self)

    def viz(self, read_order=False, form_tag=False) -> Optional[ImageType]:
        if self.image is not None:
            draw_img = copy.deepcopy(self.image)
            for idx, ann in enumerate(self.text_anns):
                if form_tag and ann.form_tag:
                    color = (255, 0, 0)
                else:
                    color = (0, 255, 0)
                draw_img = cv2.polylines(
                    draw_img,
                    [np.array(ann.abs_coord, np.int32)],
                    True, color, 2
                )
                if read_order:
                    org = (int(ann.abs_coord[0][0]), int(ann.abs_coord[0][1]))
                    draw_img = cv2.putText(
                        draw_img, str(idx), org,
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2
                    )
            return draw_img
        return None
