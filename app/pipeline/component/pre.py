from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from pipeline.base_obj import PreProcessComponent
from pipeline.config.analyze_config import AnalyzeConfig
from pipeline.data_obj.datapoint import DataPoint

IMAGE_EXTENSIONS = [
    '.jpg', '.png', '.jpeg', '.tif', '.tiff', '.bmp', '.jpe', '.jpeg', '.jp2', '.webp',
    '.pbm', '.pgm', '.ppm', '.pxm', '.pnm', '.sr', '.ras', '.hdr', '.pic', '.exr'
]
NEW_IMAGE_EXTENSIONS = [
    '.heic', '.pil', '.heif'
]
DOC_EXTENSIONS = [".doc", ".docx"]
EXCEL_EXTENSIONS = [".xls", ".xlsx"]


def convert_new_image_format(path):
    suffix = path.suffix.lower()
    # if suffix in ['.heic', '.heif']:
    #     heif_file = pyheif.read(str(path))
    #     img = Image.frombytes(
    #         heif_file.mode, heif_file.size, heif_file.data,
    #         "raw", heif_file.mode, heif_file.stride
    #     )
    #     return np.array(img)

    if suffix == '.pil':
        img = Image.open(str(path))
        img = img.convert('RGB')
        return np.array(img)
    else:
        raise ValueError("Not supported file type")


class LoadImageComponent(PreProcessComponent):

    def serve(self, path, analyze_config=None) -> DataPoint:
        if path is None:
            raise ValueError("Pass either path as argument")

        if analyze_config is None:
            analyze_config = AnalyzeConfig()

        if isinstance(path, str):
            path = Path(path)
        elif not isinstance(path, Path):
            raise ValueError("Path must be either str or Path")

        if path.is_dir():
            raise ValueError("Haven't supported directory yet")
        if not path.is_file():
            raise ValueError("Not a file")

        suffix = path.suffix.lower()
        if suffix in IMAGE_EXTENSIONS:
            # img = cv2.imread(str(path))
            img = cv2.imdecode(np.fromfile(str(path), dtype=np.uint8), cv2.IMREAD_COLOR)
        elif suffix in NEW_IMAGE_EXTENSIONS:
            img = convert_new_image_format(path)
        else:
            raise ValueError("Not supported file type")

        dp = DataPoint(
            file_name=path.name,
            file_type='image',
            lang='',
            location=str(path),
            analyze_config=analyze_config,
            image=img,
            width=img.shape[1],
            height=img.shape[0]
        )
        return dp

    def health_check(self) -> bool:
        return True
