import copy

from pipeline.component.text_order.order_utils.col import check_continuous_cols
from pipeline.component.text_order.order_utils.utils import get_block_type, append_or_extend_row, find_intersect_row


def get_header_footer(cols, header_tolerance=0.15, footer_tolerance=0.85):
    cols = [sorted(col, key=lambda it: get_block_type(it).top) for col in cols]

    temp_cols = copy.deepcopy(cols)
    temp_cols, header_row = get_header(temp_cols, header_tolerance)
    if check_continuous_cols(temp_cols):
        return header_row, temp_cols, []

    temp_cols = copy.deepcopy(cols)
    temp_cols, footer_row = get_footer(temp_cols, footer_tolerance)
    if check_continuous_cols(temp_cols):
        return [], temp_cols, footer_row

    temp_cols = copy.deepcopy(cols)
    temp_cols, header_row = get_header(temp_cols, header_tolerance)
    temp_cols, footer_row = get_footer(temp_cols, footer_tolerance)
    if check_continuous_cols(temp_cols):
        return header_row, temp_cols, footer_row
    return None, None, None


def get_header(cols, header_tolerance):
    first_header_item = cols[0][0]
    second_header_item = cols[1][0]
    header_row = []
    first_cond = get_block_type(first_header_item).top < header_tolerance
    second_cond = get_block_type(second_header_item).top < header_tolerance
    if (first_cond and second_cond and
            find_intersect_row(first_header_item, [second_header_item], intersect_tolerance=0.001)):
        append_or_extend_row(header_row, first_header_item)
        append_or_extend_row(header_row, second_header_item)
        cols[0].pop(0)
        cols[1].pop(0)
    elif first_cond and get_block_type(first_header_item).bot < get_block_type(second_header_item).top:
        append_or_extend_row(header_row, first_header_item)
        cols[0].pop(0)
    elif second_cond and get_block_type(second_header_item).bot < get_block_type(first_header_item).top:
        append_or_extend_row(header_row, second_header_item)
        cols[1].pop(0)
    return cols, header_row


def get_footer(cols, footer_tolerance):
    first_footer_item = cols[0][-1] if len(cols[0]) != 0 else None
    second_footer_item = cols[1][-1] if len(cols[1]) != 0 else None
    footer_row = []
    if first_footer_item is not None and second_footer_item is not None:
        first_cond = get_block_type(first_footer_item).top > footer_tolerance
        second_cond = get_block_type(second_footer_item).top > footer_tolerance
        if (first_cond and second_cond and
                find_intersect_row(first_footer_item, [second_footer_item], intersect_tolerance=0.001)):
            append_or_extend_row(footer_row, first_footer_item)
            append_or_extend_row(footer_row, second_footer_item)
            cols[0].pop(-1)
            cols[1].pop(-1)
        elif (first_cond and
              get_block_type(first_footer_item).top > get_block_type(second_footer_item).bot):
            append_or_extend_row(footer_row, first_footer_item)
            cols[0].pop(-1)
        elif (second_cond and
              get_block_type(second_footer_item).top > get_block_type(first_footer_item).bot):
            append_or_extend_row(footer_row, second_footer_item)
            cols[1].pop(-1)
    else:
        if first_footer_item is not None and get_block_type(first_footer_item).top > footer_tolerance:
            append_or_extend_row(footer_row, first_footer_item)
            cols[0].pop(-1)
        elif second_footer_item is not None and get_block_type(second_footer_item).top > footer_tolerance:
            append_or_extend_row(footer_row, second_footer_item)
            cols[1].pop(-1)
    return cols, footer_row
