from typing import List

from common_utils.utils import round_to
from pipeline.data_obj.ann import TextBlock, TextAnn


def get_block_type(item) -> TextBlock:
    if type(item) is list:
        return item[0]
    return item


def find_intersect_row(
        ann,
        rows,
        intersect_tolerance=0.005,
        intersect_per_union_tolerance=None
):
    ann = get_block_type(ann)
    for r in rows:
        r = get_block_type(r)
        if (r.top <= ann.bot <= r.bot and round_to(r.top - ann.bot) > intersect_tolerance) \
                or (r.top <= ann.top <= r.bot and round_to(ann.top - r.bot) > intersect_tolerance) \
                or (ann.top >= r.top and ann.bot <= r.bot) or (ann.top <= r.top and ann.bot >= r.bot):
            if intersect_per_union_tolerance is not None:
                intersect_bot = min(r.bot, ann.bot)
                intersect_top = max(r.top, ann.top)
                intersect_area = intersect_bot - intersect_top
                intersect_percentage = intersect_area / ((r.bot - r.top) + (ann.bot - ann.top) - intersect_area)
                if intersect_percentage > intersect_per_union_tolerance:
                    return r
            else:
                return r
    return None


def check_lower_row(cols, row_tolerance=0.05):
    lower_rows = []
    lower_item = max([col[0] for col in cols], key=lambda it: get_block_type(it).top)
    new_cols = []
    for col in cols:
        if lower_item in col:
            new_cols.append(col)
            continue

        new_col = []
        for row in col:
            if (get_block_type(row).bot < get_block_type(lower_item).top and
                    round_to(get_block_type(row).bot - get_block_type(lower_item).top) > row_tolerance):
                lower_rows.append(row)
            else:
                new_col.append(row)
        new_cols.append(new_col)
    if lower_rows:
        new_cols.insert(0, lower_rows)
    return new_cols


def append_or_extend_row(row, item):
    if type(item) is list:
        row.extend(item)
    else:
        row.append(item)


def check_same_line(blocks, same_line_tolerance=0.01):
    ave_cent_y = sum([block.cent_y for block in blocks]) / len(blocks)
    return all([round_to(block.cent_y - ave_cent_y, 3) < same_line_tolerance for block in blocks])


def get_sorted_anns(order_blocks: List[TextBlock]) -> List[TextAnn]:
    sorted_anns = []
    for block in order_blocks:
        if len(block.anns) == 1:
            anns = block.anns
        elif len(block.anns) == 2:
            if block.anns[0].top > block.anns[1].bot or block.anns[1].top > block.anns[0].bot:
                anns = sorted(block.anns, key=lambda it: it.top)
            else:
                anns = sorted(block.anns, key=lambda it: it.left)
        else:
            anns = sorted(block.anns, key=lambda it: (it.cent_y, it.cent_x))
        sorted_anns.extend(anns)
    return sorted_anns
