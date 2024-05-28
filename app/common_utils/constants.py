ONNX_PROVIDERS = {
    "cpu": ['CPUExecutionProvider'],
    "cuda": ['TensorrtExecutionProvider', 'CUDAExecutionProvider'],
    "gpu": ['TensorrtExecutionProvider', 'CUDAExecutionProvider']
}
OPEN_CLOSE_BRACKET_REGREX = r'\(([^)]+)\)'
TITLE_INDEX_REGREX = r'^(m{0,4}(ix|iv|v?i{0,3})|([a-f]{1})|([0-9]{1}))\.?$'
ROMAN_NUMERAL_INDEX_REGREX = "^m{0,4}(cm|cd|d?c{0,3})(xc|xl|l?x{0,3})(ix|iv|v?i{0,3})\.? "
BULLET_POINT_RE = r'^[0-9]$|^[!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~]$|^[0-9][!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~]$'
OCR_VOCAB_RE = r'^[aAàÀảẢãÃáÁạẠăĂằẰẳẲẵẴắẮặẶâÂầẦẩẨẫẪấẤậẬbBcCdDđĐeEèÈẻẺẽẼéÉẹẸêÊềỀểỂễỄếẾệỆfFgGhHiIìÌỉỈĩĨíÍịỊjJkKlLmMnNoOòÒỏỎõÕóÓọỌôÔồỒổỔỗỖốỐộỘơƠờỜởỞỡỠớỚợỢpPqQrRsStTuUùÙủỦũŨúÚụỤưƯừỪửỬữỮứỨựỰvVwWxXyYỳỲỷỶỹỸýÝỵỴzZ0123456789!"#$%&''()*+,-./:;<=>?@[\]^_`{|}~ ]+$'

TEXT_REPLACEMENTS = [
    ("\x01", " "),
    (" ", " "),
    ("\t", " "),
    ("…", "..."),
    ("—", "-"),
    ("–", "-"),
    ("•", "-"),
    ("★", "-"),
    ("", "-"),
    ("", "-"),
    ("ò", "*"),
    ("⇒", "=>"),
    ("ﬁ", "fi"),
    ("�", ""),  # \x08 backspace
    ("\r", ""),
    ("", "X"),  # checkmark
    ("●", "-"),
    ("́", ""),  # dấu sắc
    ("̀", ""),  # dấu huyền
    ("̉", ""),  # dấu hỏi
    ("̣", ""),  # dấu nặng
    ("̃", ""),  # dấu ngã
]
TEXT_REPLACEMENTS_REGREX = r"[_-]{2,}"

IMG_WIDTH = 1000
IMG_HEIGHT = 600

TIME_RANGE_REGREX = r'(from|tu) [0-9\/]{4,} (to |den )?([0-9\/]{4,}|now|present|hien tai)'
LIST_VALUES = ['はい', '前、側部', 'リーン', "待機中", "モード1", "リッチ", "完了", "モードイ", '無', '制限無', '未使用',
               '正常',
               '出力無し', 'N/P', 'Value', 'P', 'No req', 'YET', 'CMPLT', 'mode 1', 'Yes']
LIST_KEY_VAL = ["%", "％", "℃", "Nm", 'mg', "N m", "N-m", "kW", "Ａ", "rpm", "mV", "mv", "Ｖ", 'v', "V", "kPa", "km", "Hz",
                "ms",
                "MPa", "g/s", 'rm', 'pm', 'r', "m", "C", 'Y', 'z', ' ']
LIST_KEY_BEGIN_SIGNAL = ['EV', 'EGR', "OCS", "MIL", "REALY", "EVAP", "O2", "エン", "吸入", "スタ", "アイ", "現在",
                         "空燃", "高圧", "基本", "DC/DC"]
LIST_KEY_OUT_SIGNAL = ['ECM']
