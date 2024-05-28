import pkgutil
import os


class OperatorGroup:
    def __init__(self, *ops):
        self.ops = ops

    def __call__(self, data):
        for op in self.ops:
            data = op(data)
        return data


def get_character_dict(lang):
    path = os.path.join('../data/config', f'{lang}_dict.txt')
    # print(path)
    return pkgutil.get_data(__name__, path).decode('utf-8').splitlines()
