
def filter_result(img_list, height_threshold):
    final_img_list = []
    for l_index, line in enumerate(img_list):
        words = line.label.split()
        if len(words) == 0 or abs(line.top - line.bot) < height_threshold:
            continue
        final_img_list.append(line)
    return final_img_list


def check_contain_or_start_with(text, common_str):
    if text in common_str:
        return True
    for item in common_str:
        if text.startswith(item):
            return True
    return False
