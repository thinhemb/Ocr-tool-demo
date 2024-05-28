from dataclasses import dataclass, field


@dataclass
class Tag:
    key: str
    location: str = field(default=None)
    threshold: float = field(default=None)
    value: str = field(default=None)
    match_item: str = field(default=None)
    contain_key: str = field(default=None)
        
    def to_json(self):
        return {
            "key": self.key,
            "location": self.location,
            "value": self.value
        }


@dataclass
class TextTag:
    key: str
    value: str = field(default=None)
    is_start_with: bool = field(default=False)

    def to_json(self):
        return {
            "key": self.key,
            "value": self.value
        }

    @classmethod
    def from_json(cls, json_obj):
        return cls(json_obj["key"], json_obj["value"])
