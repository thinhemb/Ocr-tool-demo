from typing import List, Union

from common_utils.utils import round_to
from pipeline.data_obj.ann import TextAnn, TextBlock


def find_intersect_in_same_row(
        index,
        sorted_blocks: Union[List[TextBlock], List[TextAnn]],
        top_bot_intersect_tolerance=0.005,
        intersect_per_union_tolerance=0.1
):
    c_b = sorted_blocks[index]
    match_indices = []
    for i, n_b in enumerate(sorted_blocks):
        if i == index:
            continue

        if (n_b.top <= c_b.bot <= n_b.bot and round_to(n_b.top - c_b.bot) > top_bot_intersect_tolerance) \
                or (n_b.top <= c_b.top <= n_b.bot and round_to(c_b.top - n_b.bot) > top_bot_intersect_tolerance) \
                or (c_b.top >= n_b.top and c_b.bot <= n_b.bot) or (c_b.top <= n_b.top and c_b.bot >= n_b.bot):
            intersect_top = max(c_b.top, n_b.top)
            intersect_bot = min(c_b.bot, n_b.bot)
            intersect_area = intersect_bot - intersect_top
            intersect_percentage = intersect_area / ((c_b.bot - c_b.top) + (n_b.bot - n_b.top) - intersect_area)
            if intersect_percentage > intersect_per_union_tolerance:
                match_indices.append(i)
    return match_indices


def get_intersect_rows(
        blocks: Union[List[TextBlock], List[TextAnn]],
        top_bot_intersect_tolerance=0.005,
        intersect_per_union_tolerance=0.1
):
    td_rows: List[TextBlock] = sorted(blocks, key=lambda it: it.top)
    rows: List[List[TextBlock]] = []
    mapped_indices = []
    for index, row in enumerate(td_rows):
        if index in mapped_indices:
            continue
        match_indices = find_intersect_in_same_row(
            index, td_rows,
            top_bot_intersect_tolerance,
            intersect_per_union_tolerance
        )

        if len(match_indices) == 0:
            rows.append([row])
            mapped_indices.append(index)
        else:
            columns_row = [row]
            mapped_indices.append(index)
            for match_index in match_indices:
                if match_index in mapped_indices:
                    continue
                columns_row.append(td_rows[match_index])
                mapped_indices.append(match_index)
            rows.append(columns_row)
    return rows


def unwind_rows(rows):
    new_rows = []
    for row in rows:
        if len(row) == 1:
            new_rows.append(row)
        elif len(row) == 2:
            first_item, second_item = row
            if first_item.left < second_item.left and second_item.right < first_item.right:
                new_rows.append([second_item])
                new_rows.append([first_item])
            elif second_item.left < first_item.left and first_item.right < second_item.right:
                new_rows.append([first_item])
                new_rows.append([second_item])
            else:
                new_rows.append(row)
        else:
            new_rows.append(row)
    return new_rows
