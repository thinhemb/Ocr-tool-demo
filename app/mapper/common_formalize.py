import re
# from unidecode import unidecode
# from datetime import datetime
from typing import Optional
import difflib

from common_utils.constants import *

# from dateutil.parser import parse

DICT_MONTH = {
    "jan": "01",
    "feb": "02",
    "mar": "03",
    "apr": "04",
    "may": "05",
    "jun": "06",
    "jul": "07",
    "aug": "08",
    "sep": "09",
    "oct": "10",
    "nov": "11",
    "dec": "12"
}


def map_signal(text):
    signal = ""
    text = text.replace("--", "ー")
    text = text.replace("一", "ー")
    text = text.replace("－", "ー")
    text = text.strip('!')
    list_key = ["!", "-", ":"]
    for item in list_key:
        if item in text:
            if item == "-":
                signal = "".join(text[text.find(item) + 1:])
            else:
                signal = text.split(item)[1]
            break
    if signal == "":
        ti = "アクテ"
        if map_double_text(text[:3], ti) > 0.9:
            signal = text[8:]
    if "0" in signal and len(signal) > 3:
        signal = signal[:-2].replace("0", 'O') + signal[-2:]

    return signal.strip()


def check_begin_signal(text):
    for item in LIST_KEY_BEGIN_SIGNAL:
        if item in text:
            return True
    return False


def map_key_begin_signal(text):
    signal = ""
    check = True
    for item in LIST_KEY_BEGIN_SIGNAL:
        if item in text:
            signal = re.search(item, text).group()
            check = False
            break
    if check:
        for item in LIST_KEY_OUT_SIGNAL:
            if item in text:
                signal = "".join(text.split(item)[1:])
                break
    return signal


def map_double_text(text1, text2):
    seq = difflib.SequenceMatcher(None, text1, text2)
    similarity = seq.ratio()
    return similarity


def map_current_situation(text):
    current = "現在の状況"
    seq = difflib.SequenceMatcher(None, text, current)
    similarity = seq.ratio()
    return similarity


def map_engine(text):
    current = "エンジン"
    seq = difflib.SequenceMatcher(None, text, current)
    similarity = seq.ratio()
    return similarity


def map_key_value(text):
    check = False
    if 'EMPO' in text:
        return True, 'はい'
    if 'TEPR' in text:
        return True, 'P'
    if len(text) > 1 and '無' in text and '制' in text:
        return True, '制限無'

    max_ = 0.5
    for item in LIST_VALUES:
        simp = map_double_text(item, text)
        if simp > max_:
            max_ = simp
            text = item
            check = True
    return check, text


def formalize_value(value):
    for item in LIST_KEY_VAL:
        if item in value:
            value = value.split(item)[0].strip()
            break
    return value


# def map_month(text):
#     others = text.split()
#     for other in others:
#         if other.isalpha():
#             for key, val in DICT_MONTH.items():
#                 if key in other:
#                     text = text.replace(other, val)
#     return text


def formalize_chassis_no(text: str) -> Optional[str]:
    if text is None:
        return None

    # text = unidecode(text)
    text = re.sub(r'\s+', ' ', text).strip()
    list_key = ["n", "N", "f", "F", "k", "K"]
    check = False
    for item in list_key:
        if item in text:
            check = True
            break
    if len(text) == 2:
        if 'f' in text:
            text += 'f'
        elif 'F' in text:
            text += 'F'
    if not check and len(text) < 5:
        text = text.replace("O", "0", -6).replace("o", "0", -6)
    elif len(text) < 5:
        text = text.replace("0", "O", -6)
    if 'l0w' in text.lower():
        text = text.replace('L0W', 'LOW')
        text = text.replace('l0w', 'low')
    return text

# def get_day_month(numbs, year, format_date):
#     if len(numbs) >= 2:
#         str_date = f"{numbs[1]} {numbs[0]}"
#     else:
#         return year
#
#     try:
#         str_date += f" {year}"
#         result_date = parse(str_date)
#         result_date = result_date.strftime(format_date)
#         return result_date
#     except:
#         return year

#
# def formalize_date(text: str, format_date="%d-%m-%Y") -> Optional[str]:
#     re_res = re.findall("(\d{2})\/(\d{2})\/(\d{4})", text)
#     if re_res:
#         try:
#             str_date = f"{re_res[0][1]}-{re_res[0][0]}-{re_res[0][2]}"
#             result_date = parse(str_date)
#             result_date = result_date.strftime(format_date)
#             return result_date
#         except:
#             pass
#
#     if not text:
#         return None
#
#     text = text.lower().strip()
#     text = re.sub(r"[^\d\w]", " ", text)
#
#     if text == "now":
#         return None
#
#     year = re.findall(r"\d{4}", text)
#     if year:
#         year = year[0]
#     else:
#         return None
#
#     text = re.sub(year, "", text)
#     text = text.strip()
#
#     text = map_month(text)
#
#     numbs = re.findall(r"\d{1,2}", text)
#     final_date = get_day_month(numbs, year, format_date)
#
#     return final_date
#

# def check_invalid_date(date_str, format_date):
#     date = datetime.strptime(date_str, format_date)
#     if date > datetime.now():
#         return True
#     if date.year < 1021:
#         return True
#     return False
#
#
# def formalize_str(text: str) -> Optional[str]:
#     if text is None:
#         return None
#     text = re.sub(r'\s+', ' ', text)
#     return text.lower().strip()


# def formalize_money_amount(text: str) -> Optional[str]:
#     if text is None:
#         return None
#     text = text.lower().replace("vnd", "").strip()
#     key_text = re.search(r"^\w+:", text)
#     if key_text and len(key_text.group(0)) > 2:
#         return None
#     items = re.split(r"[,\.]", text)
#     if len(items) > 1:
#         if len(items[-1]) == 2:
#             text = "".join(items[:-1])
#         if len(items[-1]) == 1 and items[-1] == "0":
#             text = "".join(items[:-1])
#     return re.sub(r"[^\d]", "", text)


# def check_int(value):
#     if value is None:
#         return False
#     if isinstance(value, str):
#         return value.isdigit()
#     return isinstance(value, int)
