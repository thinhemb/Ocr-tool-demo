from typing import List

from common_utils.utils import round_to
from pipeline.component.text_order.order_utils.col import get_reading_cols
from pipeline.component.text_order.order_utils.utils import get_block_type, check_lower_row, check_same_line
from pipeline.data_obj.ann import TextBlock


def rearrange_complex_row_col(
        rows: List[List[TextBlock]],
) -> List[TextBlock]:
    """
    rearrange in to multiple rows separate by row that does not intersect any other row
    with row that have intersections rearrange into multiple columns from left to right
    within column read from top to bottom
    return map from original index to rearrange read index
    """
    order_blocks: List[TextBlock] = []
    mapped_index = []
    for index, row in enumerate(rows):
        if index in mapped_index:
            continue
        if len(row) == 1:
            order_blocks.append(row[0])
        elif len(row) == 2:
            lr_cols: List[TextBlock] = sorted(row, key=lambda it: it.left)
            append_find_block_item(lr_cols, index, rows, order_blocks, mapped_index)
            order_blocks.extend(lr_cols)
        else:
            if check_same_line(row):
                rearrange_items = sorted(row, key=lambda it: it.left)
                append_find_block_item(rearrange_items, index, rows, order_blocks, mapped_index)
            else:
                cols = get_reading_cols(row)
                rearrange_items = rearrange_rows_within_cols(cols)

            order_blocks.extend(rearrange_items)
    return order_blocks


def rearrange_complex_row_col_update(
        rows: List[List[TextBlock]],
) -> List[TextBlock]:
    """
    rearrange in to multiple rows separate by row that does not intersect any other row
    with row that have intersections rearrange into multiple columns from left to right
    within column read from top to bottom
    return map from original index to rearrange read index
    """
    order_blocks: List[TextBlock] = []
    mapped_index = []
    for index, row in enumerate(rows):
        if index in mapped_index:
            continue
        if len(row) == 1:
            order_blocks.append(row[0])
        elif len(row) == 2:
            lr_cols: List[TextBlock] = sorted(row, key=lambda it: it.left)
            order_blocks.extend(lr_cols)
        else:
            if check_same_line(row):
                rearrange_items = sorted(row, key=lambda it: it.left)
            else:
                cols = get_reading_cols(row)
                rearrange_items = rearrange_rows_within_cols(cols)

            order_blocks.extend(rearrange_items)
    return order_blocks


def _find_block_item(items, nex_item, prev=False, tolerance=0.05):
    for index, item in enumerate(items):
        if prev:
            if abs(item.left - nex_item.left) < tolerance and abs(item.top - nex_item.bot) < tolerance:
                return index
        else:
            if abs(item.left - nex_item.left) < tolerance and abs(item.bot - nex_item.top) < tolerance:
                return index
    return None


def append_find_block_item(rearrange_items, index, rows, order_blocks, mapped_index):
    if index != 0 and index - 1 not in mapped_index and len(rows[index - 1]) == 1:
        prev_item = rows[index - 1][0]
        found_index = _find_block_item(rearrange_items, prev_item, prev=True)
        if found_index is not None:
            rearrange_items.insert(found_index, prev_item)
            order_blocks.pop()

    if len(rows) > index + 1 and len(rows[index + 1]) == 1:
        nex_item = rows[index + 1][0]
        found_index = _find_block_item(rearrange_items, nex_item)
        if found_index is not None:
            if found_index + 1 < len(rearrange_items) and nex_item.right > rearrange_items[found_index + 1].left:
                return
            rearrange_items.insert(found_index + 1, nex_item)
            mapped_index.append(index + 1)


def _find_same_row_within_cols(cur_item, cols, cur_col_i, same_line_tolerance=0.015):
    found_indices = []
    for col_i in range(cur_col_i + 1, len(cols)):
        col = cols[col_i]
        for item_i, item in enumerate(col):
            if (round_to(item.top - cur_item.top) < same_line_tolerance or
                    round_to(item.bot - cur_item.bot) < same_line_tolerance):
                found_indices.append((col_i, item_i))
                break
    return found_indices


def find_row_by_thresh(bot, row_threshold):
    for row_i, thresh in enumerate(row_threshold):
        if bot < thresh:
            if row_i == 0:
                return -1
            else:
                return row_i - 1
    return len(row_threshold) - 1


def rearrange_rows_within_cols(cols):
    if all([len(c) == 1 for c in cols]):
        return [c[0] for c in cols]

    rows = []
    mapped_indices = []

    min_second_col = min([i.left for i in cols[1]]) if len(cols) > 1 and len(cols[1]) > 1 else None
    for item_i, item in enumerate(cols[0]):
        if ((hasattr(item, 'mapped_row') and item.mapped_row) or
                (min_second_col is not None and item.right > min_second_col)):
            rows.append([[item]])
            mapped_indices.append((0, item_i))
            continue
        found_indices = _find_same_row_within_cols(item, cols, 0)
        if found_indices and len(found_indices) == len(cols) - 1 and \
                all([i not in mapped_indices for i in found_indices]):
            row = [[item]]
            found_items = [[cols[c_i][i_i]] for (c_i, i_i) in found_indices]
            row.extend(found_items)
            rows.append(row)

            mapped_indices.append((0, item_i))
            mapped_indices.extend(found_indices)

    rearrange_items = []
    if rows:
        row_threshold = [min([i.top for i in row[0]]) for row in rows]

        head_row = []
        for col_i, col in enumerate(cols):
            for item_i, item in enumerate(col):
                if (col_i, item_i) in mapped_indices:
                    continue

                idx = find_row_by_thresh(item.top, row_threshold)
                if idx == -1:
                    head_row.append(item)
                else:
                    if col_i < len(rows[idx]):
                        rows[idx][col_i].append(item)
                    else:
                        rows[idx].append([item])

        if head_row:
            rearrange_items.extend(head_row)
        for row in rows:
            for col in row:
                rearrange_items.extend(col)
    else:
        for col in cols:
            for item in col:
                rearrange_items.append(item)
    return rearrange_items


def get_read_order_dict(cols, header=None, footer=None) -> List[TextBlock]:
    order_blocks: List[TextBlock] = []
    if header:
        header = sorted(header, key=lambda it: it.left)
        for item in header:
            order_blocks.append(item)

    cols = [sorted(col, key=lambda it: get_block_type(it).top) for col in cols if col]
    cols = check_lower_row(cols)
    blocks = rearrange_rows_within_cols(cols)
    order_blocks.extend(blocks)

    if footer:
        footer = sorted(footer, key=lambda it: it.left)
        for item in footer:
            order_blocks.append(item)
    return order_blocks
