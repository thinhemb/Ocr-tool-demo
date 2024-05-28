from typing import List, Union

from common_utils.utils import round_to
from pipeline.component.text_order.order_utils.utils import find_intersect_row, get_block_type
from pipeline.data_obj.ann import TextBlock, TextAnn


def get_reading_cols(
        blocks: List[TextBlock],
        left_same_col_tolerance=0.1,
        cent_same_col_tolerance=0.1,
):
    """
    Sắp xếp các block thành các cột dựa trên vị trí
    """
    if len(blocks) == 0:
        return []
    lr_cols = sorted(blocks, key=lambda it: it.left)
    cols = []
    sub_col = []
    for index, col in enumerate(lr_cols):
        if index == 0:
            sub_col.append(col)
        else:
            first_condition = abs(col.left - lr_cols[index - 1].left) < left_same_col_tolerance
            second_condition = abs(col.cent_x - lr_cols[index - 1].cent_x) < cent_same_col_tolerance
            if first_condition or second_condition:
                sub_col.append(col)
            else:
                # rearrange from up to down
                ud_col = sorted(sub_col, key=lambda it: it.top)
                cols.append(ud_col)
                sub_col = [col]
    ud_col = sorted(sub_col, key=lambda it: it.top)
    cols.append(ud_col)
    return cols


def check_all_not_intersect(cols):
    for i in range(len(cols) - 1):
        if any([find_intersect_row(col, cols[i + 1]) is not None for col in cols[i]]):
            return False
    return True


# cur_row.bot + cur_row.height: mean first item has 2 line
def find_same_line_in_diff_row(
        cur_row: TextBlock,
        rows,
        intersect_tolerance=0.0075,
        bot_new_line_tolerance=0.02,
        left_right_tolerance=0.3,
):
    for i, row in enumerate(rows):
        if type(row) is list:
            r = row[0]
        else:
            r = row
        if (round_to(r.left - cur_row.right, 2) <= left_right_tolerance or
                round_to(r.right - cur_row.left, 2) <= left_right_tolerance):
            if (round_to(r.top - cur_row.top, 3) <= intersect_tolerance and
                    round_to(r.bot - cur_row.bot, 3) <= bot_new_line_tolerance):
                return i
            if (round_to(r.top - cur_row.bot) <= intersect_tolerance or
                    round_to(r.bot - cur_row.top) <= intersect_tolerance):
                return i
    return None


# Remove cols contain only line
def unwind_cols(cols):
    if check_all_not_intersect(cols):
        all_col = []
        for col in cols:
            all_col.extend(col)
        all_col = sorted(all_col, key=lambda it: it.top)
        return [all_col]

    sub_indices = [i for i, col in enumerate(cols) if len(col) <= 5 and all([len(r.anns) <= 2 for r in col])]
    suc_merge_cols = []
    if sub_indices:
        if len(sub_indices) == len(cols):
            min_len = max([len(col) for col in cols])
            min_index = 0
            for index, col in enumerate(cols):
                if len(col) < min_len:
                    min_len = len(col)
                    min_index = index
            sub_indices = [min_index]

        main_indices = [i for i, col in enumerate(cols) if i not in sub_indices]
        for sub_i in sub_indices:
            for main_i in main_indices:
                map_indices = [find_same_line_in_diff_row(r, cols[main_i]) for r in cols[sub_i]]
                if all([i is not None for i in map_indices]):
                    for sub_item in cols[sub_i]:
                        map_index = find_same_line_in_diff_row(sub_item, cols[main_i])
                        main_item = cols[main_i][map_index]
                        if type(main_item) is tuple:
                            cols[main_i][map_index] = [cols[main_i][map_index], sub_item]
                        elif type(main_item) is list:
                            cols[main_i][map_index].append(sub_item)
                        elif type(main_item) is TextBlock:
                            cols[main_i][map_index].update_child(sub_item)
                    suc_merge_cols.append(sub_i)
                    break
        return [col for i, col in enumerate(cols) if i not in suc_merge_cols]
    return cols


def check_continuous_cols(cols, col_left_tolerance=0.15, col_right_tolerance=0.5):
    for col in cols:
        col = sorted(col, key=lambda it: get_block_type(it).top)
        if len(col) < 2:
            continue
        for i in range(len(col) - 1):
            cur_item = get_block_type(col[i])
            nex_item = get_block_type(col[i + 1])
            first_cond = round_to(cur_item.left - nex_item.left) > col_left_tolerance
            second_cond = round_to(cur_item.right - nex_item.right) > col_right_tolerance
            if first_cond or second_cond:
                return False
    return True


def find_intersect_in_same_col(
        index,
        sorted_blocks: Union[List[TextBlock], List[TextAnn]],
        left_right_intersect_tolerance=0.01,
        intersect_per_union_tolerance=0.1
):
    c_b = sorted_blocks[index]

    match_indices = []
    for i, n_b in enumerate(sorted_blocks):
        if i == index:
            continue

        if (n_b.left <= c_b.right <= n_b.right and round_to(n_b.left - c_b.right) > left_right_intersect_tolerance) \
                or (n_b.left <= c_b.left <= n_b.right
                    and round_to(c_b.left - n_b.right) > left_right_intersect_tolerance):
            intersect_top = max(c_b.left, n_b.left)
            intersect_bot = min(c_b.right, n_b.right)
            intersect_area = intersect_bot - intersect_top
            intersect_percentage = intersect_area / ((c_b.right - c_b.left) + (n_b.right - n_b.left) - intersect_area)
            if intersect_percentage > intersect_per_union_tolerance:
                match_indices.append(i)

        if (c_b.left >= n_b.left and c_b.right <= n_b.right) or \
                ((c_b.left <= n_b.left or round_to(c_b.left - n_b.left) < left_right_intersect_tolerance) and
                 (c_b.right >= n_b.right or round_to(c_b.right - n_b.right) < left_right_intersect_tolerance)):
            match_indices.append(i)
    return match_indices


def get_intersect_cols(
        blocks: Union[List[TextBlock], List[TextAnn]],
        left_right_intersect_tolerance=0.01,
        intersect_per_union_tolerance=0.1
):
    sorted_blocks = sorted(blocks, key=lambda it: it.width, reverse=True)
    cols = []
    mapped_indices = []
    for index, block in enumerate(sorted_blocks):
        if index in mapped_indices:
            continue
        match_indices = find_intersect_in_same_col(
            index, sorted_blocks,
            left_right_intersect_tolerance,
            intersect_per_union_tolerance
        )

        if len(match_indices) == 0:
            cols.append([block])
            mapped_indices.append(index)
        else:
            col = [block]
            mapped_indices.append(index)
            for match_index in match_indices:
                if match_index in mapped_indices:
                    continue
                col.append(sorted_blocks[match_index])
                mapped_indices.append(match_index)
            cols.append(col)
    return cols
