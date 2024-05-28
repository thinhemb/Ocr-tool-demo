import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from pipeline.config.tag import Tag
from pipeline.utils.datatypes import ImageType


@dataclass
class Ann:
    annotation_id: str = field(init=False, default_factory=lambda: str(uuid.uuid1()), repr=False)
    rel_coord: list = field(default_factory=list, repr=False)
    is_abs: bool = field(default=False, repr=False)
    abs_coord: list = field(default_factory=list, repr=False)

    @classmethod
    def from_abs_coord(cls, abs_coord, width, height):
        rel_coord = [
            [abs_coord[0][0] / width, abs_coord[0][1] / height],
            [abs_coord[1][0] / width, abs_coord[1][1] / height],
            [abs_coord[2][0] / width, abs_coord[2][1] / height],
            [abs_coord[3][0] / width, abs_coord[3][1] / height]
        ]
        return cls(rel_coord=rel_coord, abs_coord=abs_coord)

    @property
    def left(self):
        if self.is_abs and self.abs_coord:
            return self.abs_coord[0][0]
        return self.rel_coord[0][0]

    @property
    def right(self):
        if self.is_abs and self.abs_coord:
            return self.abs_coord[1][0]
        return self.rel_coord[1][0]

    @property
    def width(self):
        if self.is_abs and self.abs_coord:
            return self.abs_coord[1][0] - self.abs_coord[0][0]
        return self.rel_coord[1][0] - self.rel_coord[0][0]

    @property
    def cent_x(self):
        if self.is_abs and self.abs_coord:
            return (self.abs_coord[0][0] + self.abs_coord[1][0]) / 2
        return (self.rel_coord[0][0] + self.rel_coord[1][0]) / 2

    @property
    def top(self):
        if self.is_abs and self.abs_coord:
            return self.abs_coord[0][1]
        return self.rel_coord[0][1]

    @property
    def bot(self):
        if self.is_abs and self.abs_coord:
            return self.abs_coord[3][1]
        return self.rel_coord[3][1]

    @property
    def height(self):
        if self.is_abs and self.abs_coord:
            return self.abs_coord[3][1] - self.abs_coord[0][1]
        return self.rel_coord[3][1] - self.rel_coord[0][1]

    @property
    def cent_y(self):
        if self.is_abs and self.abs_coord:
            return (self.abs_coord[0][1] + self.abs_coord[3][1]) / 2
        return (self.rel_coord[0][1] + self.rel_coord[3][1]) / 2

    @property
    def coord_rect(self):
        return [self.left, self.top, self.right, self.bot]


@dataclass
class TextAnn(Ann):
    img: ImageType = field(default=None, repr=False)
    label: str = None
    prob: float = None
    # lang: str = "japan"
    form_tag: Tag = None
    is_mapped: bool = False
    merged_anns: List["TextAnn"] = field(default_factory=list, repr=False)

    @classmethod
    def from_coord_and_img(cls, abs_coord, width, height, img):
        instance = super().from_abs_coord(abs_coord, width, height)
        instance.img = img
        return instance

    @classmethod
    def from_coord_img_label(cls, abs_coord, width, height, img, label, prob, form_tag=None):
        instance = super().from_abs_coord(abs_coord, width, height)
        instance.img = img
        instance.label = label.strip()
        instance.form_tag = form_tag
        instance.prob = prob
        return instance

    @classmethod
    def from_coord_and_label(cls, abs_coord, width, height, label, form_tag=None):
        instance = super().from_abs_coord(abs_coord, width, height)
        instance.label = label
        instance.form_tag = form_tag
        return instance

    @property
    def get_img(self):
        return self.img

    def to_json(self):
        return {
            "coord": self.abs_coord,
            "label": self.label,
            "prob": self.prob,
            # "lang": self.lang,
            "form_tag": self.form_tag.to_json() if self.form_tag else None
        }


class LayoutType:
    """Layout types"""

    table = "TABLE"
    figure = "FIGURE"
    list = "LIST"
    text = "TEXT"
    title = "TITLE"
    logo = "LOGO"
    signature = "SIGNATURE"
    caption = "CAPTION"
    footnote = "FOOTNOTE"
    formula = "FORMULA"
    page_footer = "PAGE-FOOTER"
    page_header = "PAGE-HEADER"
    section_header = "SECTION_HEADER"
    page = "PAGE"
    cell = "CELL"
    row = "ROW"
    column = "COLUMN"
    word = "WORD"
    line = "LINE"


@dataclass
class LayoutAnn(Ann):
    img: ImageType = field(default=None, repr=False)
    layout_type: str = None
    prob: float = 1.0

    @classmethod
    def from_coord_and_type(cls, abs_coord, width, height, layout_type):
        instance = super().from_abs_coord(abs_coord, width, height)
        instance.layout_type = layout_type
        return instance


@dataclass
class TableCell:
    text: str = None
    col_span: int = 1
    row_span: int = 1


@dataclass
class TableAnn(Ann):
    img: ImageType = field(default=None, repr=False)
    headers: List[TextAnn] = field(default_factory=list)
    data: List[List[TextAnn]] = field(default_factory=list)
    footers: List[List[TextAnn]] = field(default_factory=list)

    @classmethod
    def from_coord_and_img(cls, abs_coord, img, width, height):
        instance = super().from_abs_coord(abs_coord, width, height)
        instance.img = img
        return instance


@dataclass
class TextBlock(Ann):
    latest_line_top: float = field(default=0.0, repr=False)

    anns: List[TextAnn] = field(default_factory=list)
    texts: List[str] = field(default_factory=list)

    img: ImageType = field(default=None, repr=False)
    mapped_row: Optional[bool] = False

    @classmethod
    def from_ann(cls, text_ann: TextAnn) -> "TextBlock":
        return cls(rel_coord=text_ann.rel_coord, abs_coord=text_ann.abs_coord, latest_line_top=text_ann.top,
                   anns=[text_ann], texts=[text_ann.label])

    @classmethod
    def from_anns(cls, text_anns: List[TextAnn]) -> "TextBlock":
        left = min([ann.left for ann in text_anns])
        right = max([ann.right for ann in text_anns])
        top = min([ann.top for ann in text_anns])
        bot = max([ann.bot for ann in text_anns])
        rel_coord = [[left, top], [right, top], [right, bot], [left, bot]]
        texts = [ann.label for ann in text_anns]

        return cls(rel_coord=rel_coord, latest_line_top=top, anns=text_anns, texts=texts)

    def update_coord(self, text_ann: TextAnn):
        top = min(self.top, text_ann.top)
        bot = max(self.bot, text_ann.bot)
        left = min(self.left, text_ann.left)
        right = max(self.right, text_ann.right)

        self.rel_coord = [[left, top], [right, top], [right, bot], [left, bot]]
        self.latest_line_top = text_ann.top
        self.anns.append(text_ann)
        self.texts.append(text_ann.label)

    def update_child(self, c_block: "TextBlock"):
        for ann in c_block.anns:
            if ann not in self.anns:
                self.anns.append(ann)
                self.texts.append(ann.label)

    def to_img(self, img: ImageType):
        h, w, _ = img.shape
        left = int(self.left * w)
        right = int(self.right * w)
        top = int(self.top * h)
        bot = int(self.bot * h)
        self.img = img[top:bot, left:right]
