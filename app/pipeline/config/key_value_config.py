import json
from dataclasses import dataclass, field
from typing import Dict, List

from common_utils.string_utils import normalize_str, similar
from common_utils.constants import *
from pipeline.config.tag import Tag


@dataclass
class KeyValueConfig:
    key_value_map: Dict = field(default_factory=dict)
    common_str: List[str] = field(default_factory=list)
    threshold: float = 0.92

    @classmethod
    def from_json(cls, config_path):
        with open(config_path, 'r', encoding='utf8') as f:
            config = json.load(f)
        common_str = []
        if "common_str" in config:
            common_str = config.pop('common_str')
        threshold = 0.9
        if "threshold" in config:
            threshold = config.pop('threshold')
        return cls(config, common_str, threshold)

    def compare(self, text, norm_text, item):
        if len(text) - len(item) > 3:
            if norm_text.startswith(item + " "):
                return True
            if similar(item, norm_text) >= self.threshold:
                return True
            if similar(item, text) >= self.threshold:
                return True
            if len(norm_text.split()) - len(item.split()) > 5:
                short_text = " ".join(norm_text.split()[:len(item.split())])
                if similar(item, short_text) >= self.threshold:
                    return True
        return False

    @staticmethod
    def contain_key(text, item):
        if item in text[:len(item)]:
            return True
        return False

    def find_key_value(self, text):
        check_list_val = text.split()
        for key in LIST_KEY_VAL:
            if key in check_list_val:
                return None
        norm_text = normalize_str(text)
        # norm_text = normalize_str(text, remove_digit=True, remove_roman_numeral=True)
        for key, value in self.key_value_map.items():
            for item in value["texts"]:
                if "location" in value:
                    if value["location"] == "in" and self.contain_key(norm_text, item.lower()):
                        location = value["location"] if "location" in value else None
                        threshold = value["threshold"] if "threshold" in value else None
                        return Tag(key=key, location=location, threshold=threshold, contain_key=item)
                if self.compare(text, norm_text, item):
                    if value["location"] == "right":
                        res_value = text[len(item):].strip()
                        idx = max(
                            [res_value.rfind("-"), res_value.rfind(":")])
                        if idx != -1:
                            if res_value.startswith("-"):
                                res_value = res_value[2:]
                            elif res_value.startswith(":"):
                                res_value = res_value[2:]
                            elif idx == len(res_value) - 1:
                                threshold = value["threshold"] if "threshold" in value else None
                                return Tag(key=key, location=value["location"], threshold=threshold, match_item=item)
                            else:
                                res_value = res_value[idx + 1:].strip()

                        return Tag(key=key, value=res_value, match_item=item)
                    else:
                        location = value["location"] if "location" in value else None
                        threshold = value["threshold"] if "threshold" in value else None
                        return Tag(key=key, location=location, threshold=threshold, match_item=item)

                # if similar(item, text) >= self.threshold or similar(item, norm_text) >= self.threshold:
                if similar(item, norm_text) >= self.threshold:
                    threshold = value["threshold"] if "threshold" in value else None
                    location = value["location"] if "location" in value else None
                    return Tag(key=key, location=location, threshold=threshold, match_item=item)
        return None
