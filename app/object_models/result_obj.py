import json
from dataclasses import dataclass, field
from typing import List


@dataclass
class ResultObj:
    NER_NAME_MAP = {}

    def add_field(self, key, value):
        setattr(self, key, value)

    def to_dict(self, indent=None):
        dict_obj = {}
        for key, values in self.__dict__.items():
            if isinstance(values, list):
                dict_obj[key] = [i.to_dict() if hasattr(i, "to_dict") else i for i in values]
            else:
                dict_obj[key] = values.to_dict() if hasattr(values, "to_dict") else values
        if indent is not None:
            return json.dumps(dict_obj, indent=indent, ensure_ascii=False)
        return dict_obj

    def load_from_dict(self, result):
        for key, value in result.items():
            setattr(self, key, value)

    def ser_ner_value(self, field_, value):
        if field_ not in self.NER_NAME_MAP:
            raise Exception(f"Field {field_} not found in Ner_Name_MAP")
        field_name = self.NER_NAME_MAP[field_]
        if not hasattr(self, field_name):
            if isinstance(getattr(self, field_name), list):
                if isinstance(value, list):
                    for v in value:
                        if v not in getattr(self, field_name):
                            getattr(self, field_name).append(v)
                else:
                    if value not in getattr(self, field_name):
                        getattr(self, field_name).append(value)
            else:
                setattr(self, field_name, value)

    def has_ner_field(self, field_):
        if field_ not in self.NER_NAME_MAP:
            raise Exception(f"Field {field_} not found in NER_NAME_MAP")
        field_name = self.NER_NAME_MAP[field_]
        if not hasattr(self, field_name):
            return False
        value = getattr(self, field_name)
        return value is None or isinstance(value, list)


@dataclass
class TableInfo(ResultObj):
    name_image: str = None
    type_image: str = None
    list_signals_values: List[dict] = field(default_factory=list)
