from dataclasses import dataclass


@dataclass
class AnalyzeConfig:
    """Configuration for runtime. Inherit from this class to add more config"""
    max_datapoints: int = 5

    corner_detection: bool = False
    # OCR
    vertical_tolerance: float = 0.4
    ocr_prob_threshold: float = 0.3
    ocr_height_threshold: float = 0.0075

    # Result
    return_mapped_result: bool = True

    return_train_data: bool = False
