import numpy as np
from typing import List

from pipeline.base_obj import PostProcessComponent
from object_models.result_obj import TableInfo
from pipeline.data_obj.ann import TextAnn
from pipeline.data_obj.datapoint import DataPoint
from mapper.common_formalize import map_key_begin_signal, map_signal, map_current_situation, \
    formalize_value, formalize_chassis_no, map_key_value, map_engine
from mapper.mapper_signal import load_list_key_signal, map_list_keys_signal
from common_utils.string_utils import similar


class TableMapper(PostProcessComponent):
    def __init__(self, lang):
        self.list_keys_signal = load_list_key_signal(lang)

    def serve(self, dps: List[DataPoint]):
        result = TableInfo()

        for p_idx, dp in enumerate(dps):
            try:
                result.name_image = dp.location
                result.type_image = dp.type_image
                if dp.type_image == "0":
                    result.list_signals_values = self.process_text_type_0(dp.image, dp.text_anns)
                elif dp.type_image == "1":
                    result.list_signals_values = self.process_text_type_1(dp.image, dp.text_anns)
                elif dp.type_image in ["2", "4", "5"]:
                    result.list_signals_values = self.process_text_type_2_4_5(dp.text_anns)
                elif dp.type_image == "3":
                    result.list_signals_values = self.process_text_type_3(dp.text_anns)
            except Exception as err:
                print(err)
        return result

    def get_signal(self, text, img, text_ann, flag_begin):
        if flag_begin:
            flag = self.check_flag_status_signal(img, text_ann)
            if flag:
                signal = map_signal(text)
                signal = map_list_keys_signal(self.list_keys_signal, signal)
                return signal
        return None

    def process_text_type_0(self, img, text_anns: list[TextAnn]):
        res = []
        for idx, text_ann in enumerate(text_anns):
            text, flag_begin = self.get_text(text_ann)
            signal = self.get_signal(text, img, text_ann, flag_begin)
            if signal is not None:
                for index in range(idx + 1, len(text_anns)):
                    check_value = self.check_value_down(text_ann, text_anns[index])
                    if check_value:
                        val = text_anns[index].label.strip()
                        check, value = map_key_value(val)
                        if not check:
                            value = formalize_chassis_no(formalize_value(val))
                        res.append({"signal": signal, "value": value, "status_log": False})
                        break
        return res

    def process_text_type_1(self, img, text_anns: list[TextAnn]):
        res = []
        for idx, text_ann in enumerate(text_anns):
            text, flag_begin = self.get_text(text_ann)
            signal = self.get_signal(text, img, text_ann, flag_begin)
            if signal is not None:
                val = text_anns[idx + 1].label.strip()
                check, value = map_key_value(val)
                if not check:
                    value = formalize_chassis_no(formalize_value(val))
                res.append({"signal": signal, "value": value, "status_log": False})
        return res

    def process_text_type_3(self, text_anns: list[TextAnn]):
        res = []
        for idx, text_ann in enumerate(text_anns):
            text = self.get_text(text_ann)
            if map_engine(text) >= 0.5:
                signal = text_anns[idx + 1].label.strip()
                signal = map_list_keys_signal(self.list_keys_signal, signal)
                if signal == "":
                    signal = text
                val = text_anns[idx + 2].label.strip()
                check, value = map_key_value(val)
                if not check:
                    value = formalize_chassis_no(formalize_value(val))
                res.append({"signal": signal, "value": value, "status_log": False})
        return res

    def process_text_type_2_4_5(self, text_anns: list[TextAnn]):
        signal = ""
        value = ""
        check_val = True
        for idx, text_ann in enumerate(text_anns):
            text = self.get_text(text_ann)
            if idx == 0:
                signal = map_signal(text)
                if signal == "":
                    signal = map_key_begin_signal(text)
                signal = map_list_keys_signal(self.list_keys_signal, signal)
                if signal == "":
                    signal = text
            else:
                if similar(signal, text) > 0.7:
                    value = formalize_chassis_no(formalize_value(text_anns[idx + 1].label.strip()))
                    check_val = False
                    break
        if check_val:
            for idx, text_ann in enumerate(text_anns):
                text = self.get_text(text_ann)
                if map_current_situation(text) > 0.5:
                    val = text_anns[idx + 1].label.strip()
                    check, value = map_key_value(val)
                    if not check:
                        value = formalize_chassis_no(formalize_value(val))
                    break
        return [{"signal": signal, "value": value, "status_log": False}]

    @staticmethod
    def get_text(text_ann):
        text = text_ann.label.strip()
        if text_ann.form_tag:
            if text_ann.form_tag.contain_key:
                text = text
            elif text_ann.form_tag.value:
                text = text_ann.form_tag.value.strip()
            if text_ann.form_tag.location is not None:
                return text, True
        return text, False

    @staticmethod
    def check_flag_status_signal(img, text_ann):
        point_left_top = text_ann.abs_coord[0]
        point_right_bottom = text_ann.abs_coord[2]
        # print(point_left_top, point_right_bottom)
        w, h = img.shape[:2]
        img_data = np.array(img)

        pixel_left_top = img_data[(min(int(point_left_top[1]), w - 5)), min(int(point_left_top[0]), h - 5)]
        b_left, g_left, r_left = pixel_left_top

        pixel_right_bottom = img_data[
            (min(int(point_right_bottom[1]), w - 5)), min(int(point_right_bottom[0]), h - 5)]
        b_right, g_right, r_right = pixel_right_bottom
        if ((r_left > g_left and r_left > b_left) or (r_right > g_right and r_right > b_right)) and (
                r_right > 180 or r_left > 180):
            return False
        return True

    def check_value_down(self, text_ann, text_ann_value):
        abs_coord = text_ann.abs_coord
        abs_coord_value = text_ann_value.abs_coord
        return self.rect_in_rect(abs_coord, abs_coord_value)

    @staticmethod
    def rect_in_rect(abs_coord, abs_coord_value):
        x0, y0 = abs_coord[0][0] + 200, abs_coord[0][1] + 40
        x2, y2 = abs_coord[2][0] + 500, abs_coord[2][1] + 100

        if (x0 <= abs_coord_value[0][0]
                and y0 <= abs_coord_value[0][1]
                and x2 >= abs_coord_value[2][0]
                and y2 >= abs_coord_value[2][1]):
            return True
        return False

    def health_check(self) -> bool:
        return True
