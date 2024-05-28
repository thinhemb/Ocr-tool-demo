import json


class Config:
    def __init__(self, type_):
        self.type = type_
        self.path_file = ""
        self.choose_config()
        self.data = ""
        self.read_config_json()

    def read_config_json(self):
        with open(self.path_file, "r", encoding='utf-8') as file:
            data_str = file.read()
            data = json.loads(data_str)
            self.data = self.check_data(data)

    # // "char_dict": "data\\config\\japan_dict.txt",
    def get_json(self):
        return self.data

    def choose_config(self):

        if self.type == 'ppocr':
            self.path_file = "data/config/config_ocr.json"
        elif self.type == 'yolo_det':
            self.path_file = "data/config/config_yolo_det.json"
        # else:
        #     pass

    def check_data(self, data):
        if self.type == 'ppocr':
            data = check_data_ocr(data)
        elif self.type == 'yolo_det':
            data = check_data_yolo_det(data)
        else:
            pass
        return data


def check_data_yolo_det(data):
    if data["model_dir"] is None:
        data["model_dir"] = "..\\data\\infer"
    if data["confidence_threshold"] is None:
        data["confidence_threshold"] = 0.5
    if data["iou_threshold"] is None:
        data["iou_threshold"] = 0.4
    return data


def check_data_ocr(data):
    if data["det"] is None:
        data["det"] = "data\\infer\\det\\onnx\\det_ppocr_v4.onnx"
    if data["rec_japan"] is None:
        data["rec_japan"] = "data\\infer\\rec\\onnx\\rec_jpn_ppocr_v3.onnx"
    if data["rec_en"] is None:
        data["rec_en"] = "data\\infer\\rec_en\\onnx\\rec_en_ppocr_v4.onnx"
    return data
