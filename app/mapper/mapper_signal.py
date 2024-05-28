import pandas as pd

from mapper.common_formalize import map_double_text

PATH_LIST_SIGNAL = r"data\config\list_signal.xlsx"


def map_list_keys_signal(list_keys_signal, text):
    signal = text
    max_ = 0.4
    for key in list_keys_signal:
        if abs(len(text) - len(key)) < 5:
            similarity = map_double_text(text, key)
            if similarity > max_:
                max_ = similarity
                signal = key
                if max_ == 1.0:
                    break
    return signal


def load_list_key_signal(lang):
    df = pd.read_excel(PATH_LIST_SIGNAL)
    list_keys_signal = []
    if lang == 'japan':
        list_keys_signal = df["JAPAN"].dropna().tolist()
    list_keys_signal.extend(df['EN'].dropna().tolist())
    # print(len(list_keys_signal))
    return list_keys_signal


# if __name__ == "__main__":
#     load_list_key_signal()
