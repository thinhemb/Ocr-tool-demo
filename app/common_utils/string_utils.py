from __future__ import print_function
# from spellchecker import SpellChecker
import re
from difflib import SequenceMatcher


from common_utils.constants import OPEN_CLOSE_BRACKET_REGREX, ROMAN_NUMERAL_INDEX_REGREX, BULLET_POINT_RE, OCR_VOCAB_RE


def normalize_str(string, ignore_str=None,
                  remove_digit=False,
                  remove_roman_numeral=False,
                  remove_alphabet_numbering=False,
                  remove_open_close_bracket=False,
                  min_len=None, keep_space=False):
    if ignore_str is None:
        ignore_str = []
    if string is None:
        return None
    if ignore_str:
        for s in ignore_str:
            if s in string:
                string = string.replace(s, "").strip()
    if min_len:
        string = " ".join([w for w in string.split(" ") if len(w) >= min_len])

    # string = unidecode(string.lower())
    # string = string.lower()
    string = string.upper()
    if remove_roman_numeral:
        string = re.sub(ROMAN_NUMERAL_INDEX_REGREX, ' ', string)
    if remove_alphabet_numbering:
        string = re.sub('^[a-f]{1}\. ', ' ', string)
    if remove_open_close_bracket:
        string = re.sub(OPEN_CLOSE_BRACKET_REGREX, ' ', string)

    if remove_digit:
        string = re.sub('[^a-zA-Z]', ' ', string)
    # else:
    #     string = re.sub('[^a-zA-Z0-9]', ' ', string)

    if not keep_space:
        string = re.sub(' +', ' ', string)
    return string.strip()


def is_bullet_point(text):
    return re.match(BULLET_POINT_RE, text.strip())


def is_vietnamese(text):
    return re.match(OCR_VOCAB_RE, text)


def find_match_percentage(key_word, text):
    ratio = SequenceMatcher(None, key_word, text).ratio()
    if ratio >= 0.9:
        return ""
    key_len = len(key_word.split())
    text_len = len(text.split())
    if text_len >= key_len:
        compare_str = " ".join(text.split()[0: key_len])
        ratio = SequenceMatcher(None, key_word, compare_str).ratio()
        if ratio >= 0.9:
            return " ".join(text.split()[key_len:])
    return None


def remove_accents(input_str):
    s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
    s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'
    s = ''
    input_str.encode('utf-8')
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def similar(a, b):
    if a is None or b is None:
        return 0.0
    return SequenceMatcher(None, a, b).ratio()


# TODO add ,
def remove_punctuation(input_string):
    input_string = re.sub(r'[^\w\s\.\:\-\/\(\)\@\_\+,]', ' ', input_string)
    return input_string


def clean_text(text):
    text = re.sub(r'[^\w\s]', " ", text).strip()
    text = re.sub(r'\s+', ' ', text)
    return text


def standardize_text(input_string):
    input_string = remove_punctuation(input_string)
    input_string = re.sub(r'\s+', ' ', input_string)
    input_string = input_string.strip()
    return input_string


def clean_space(text):
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'(^ )|( $)', '', text)
    text = text.replace(' \n ', '\n').replace(' \n', '\n').replace('\n ', '\n')
    return text


def get_title_min_error(titles):
    titles = sorted(titles, key=lambda x: x[list(x.keys())[0]])
    return list(titles[0].keys())[0]


def find_contain_arr(text, arr, ignore_space=False):
    text = normalize_str(text).replace(" ", "") if ignore_space else normalize_str(text)
    for item in arr:
        norm = normalize_str(item).replace(" ", "") if ignore_space else normalize_str(item)
        if norm in text:
            return item
    return None
