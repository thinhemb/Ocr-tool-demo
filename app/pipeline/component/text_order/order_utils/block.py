from typing import List

from common_utils.utils import round_to
from pipeline.component.text_order.order_utils.row import get_intersect_rows
from pipeline.data_obj.ann import TextAnn, TextBlock


def is_same_block(
        ann: TextAnn,
        block: TextBlock,
        margin_tolerance: float = 0.01,  # phần trăm căn lề trái, phải, giữa
        dif_line_tolerance: float = 0.01,  # phần trăm khoảng cách giữa 2 hàng
        same_line_top_tolerance: float = 0.005,  # phần trăm độ lệch lề trên để 2 hàng trong 1 dòng
        same_line_tolerance: float = 0.02  # phần trăm độ lệch để 2 hàng cạnh nhau
) -> bool:
    first_cond = round_to(ann.left - block.left) < margin_tolerance  # căn lề trái
    second_cond = round_to(ann.top - block.bot) < dif_line_tolerance  # khoảng cách dòng trên dưới

    # appeared to be in the same line
    third_cond = round_to(ann.top - block.latest_line_top) < same_line_top_tolerance  # độ lệch lề trên
    fourth_cond = (round_to(ann.left - block.right) < same_line_tolerance or
                   round_to(ann.right - block.left)) < same_line_tolerance  # khoảng cách trái phải cạnh nhau

    cent = (ann.left + ann.right) / 2
    fifth_condition = round_to(cent - block.cent_x) < margin_tolerance  # căn giữa

    sixth_condition = round_to(ann.right - block.right) < margin_tolerance  # căn lề phải

    return (first_cond and second_cond) or (third_cond and fourth_cond) or \
        (fifth_condition and second_cond) or (sixth_condition and second_cond)


def find_same_line_key_value(
        text_anns: List[TextAnn], cur_i,
        same_key_top_tolerance=0.05, same_key_left_tolerance=0.05, left_right_key_tolerance=0.2
):
    cur_ann = text_anns[cur_i]
    match_idx = []

    right_cond = lambda c, n: (round_to(c.cent_y - n.cent_y, 2) <= same_key_top_tolerance and
                               (n.left > c.right or round_to(c.right - n.left, 1) <= same_key_left_tolerance) and
                               round_to(c.right - n.left, 1) <= left_right_key_tolerance)
    bottom_cond = lambda c, n: (round_to(c.bot - n.top) < same_key_top_tolerance and
                                round_to(c.left - n.left, 1) <= same_key_left_tolerance)

    for j, nex_ann in enumerate(text_anns):
        if cur_i == j:
            continue

        if nex_ann.form_tag:
            continue

        if cur_ann.form_tag.location == 'right':
            if right_cond(cur_ann, nex_ann):
                match_idx.append(j)
        elif cur_ann.form_tag.location == 'bottom':
            if bottom_cond(cur_ann, nex_ann):
                match_idx.append(j)
        elif cur_ann.form_tag.location == 'bottom_or_right':
            if right_cond(cur_ann, nex_ann) or bottom_cond(cur_ann, nex_ann):
                match_idx.append(j)
        elif cur_ann.form_tag.location == 'bottom_right':
            if (round_to(abs(cur_ann.top - nex_ann.top)) < 0.02 and
                    round_to(abs(cur_ann.bot - nex_ann.bot)) < 0.02 and
                    round_to(abs(cur_ann.right - nex_ann.left), 1) <= left_right_key_tolerance):
                match_idx.append(j)
        elif cur_ann.form_tag.location == 'center':
            if (round_to(abs(cur_ann.cent_x - nex_ann.cent_x)) < 0.05
                    and round_to(abs(cur_ann.bot - nex_ann.top)) < 0.05):
                match_idx.append(j)
    return match_idx


def find_block_contain_block(blocks, block):
    for i, b in enumerate(blocks):
        if (block.top < b.top and b.bot < block.bot and
                block.left < b.left and b.right < block.right):
            return i
    return None


def merge_contained_block(
        blocks: List[TextBlock]
) -> List[TextBlock]:
    new_blocks: List[TextBlock] = []
    contained_i = []
    for p_i, p_block in enumerate(blocks):
        if p_i in contained_i:
            continue
        c_i = find_block_contain_block(blocks, p_block)
        if c_i is not None:
            c_block = blocks[c_i]
            p_block.update_child(c_block)
            new_blocks.append(p_block)
            if c_block in new_blocks:
                new_blocks.remove(c_block)
            contained_i.append(c_i)
        else:
            new_blocks.append(p_block)
    return new_blocks


def _validate_row_block(rows):
    if len(rows) > 2:
        one_col_rows = [row for row in rows if len(row) == 1]
        if len(one_col_rows) == len(rows):
            return True

        two_col_rows = [row for row in rows if len(row) == 2]
        if len(two_col_rows) == len(rows):
            return True

        if len(two_col_rows) > len(one_col_rows):
            if len(two_col_rows) < 1:
                return False
            min_second_col = min([r[1].left for r in two_col_rows])
            if all([row[0].right > min_second_col for row in one_col_rows]):
                return True
        else:
            if len(one_col_rows) < 1:
                return False
            max_one_col = max([r[0].right for r in one_col_rows])
            if all([row[1].left < max_one_col for row in two_col_rows]):
                return True
    return False


def get_row_blocks(
        text_anns: List[TextAnn],
        margin_tolerance: float = 0.01,  # phần trăm căn lề trái, phải, giữa
        dif_line_tolerance: float = 0.0075,  # phần trăm khoảng cách giữa 2 hàng
        same_line_top_tolerance: float = 0.005,  # phần trăm độ lệch lề trên để 2 hàng trong 1 dòng
        same_line_tolerance: float = 0.02,  # phần trăm độ lệch để 2 hàng cạnh nhau
) -> List[TextBlock]:
    """
    Gom các anns theo vị trí tương đối rất gần nhau ưu tiên item ngang nhau cùng hàng
    """
    rows = get_intersect_rows(text_anns)
    if _validate_row_block(rows):
        blocks = []
        for row in rows:
            block = TextBlock.from_anns(row)
            block.mapped_row = True
            blocks.append(block)
        return blocks

    blocks: List[TextBlock] = []
    for idx, text_ann in enumerate(text_anns):

        column_found = False
        for block in reversed(list(blocks)):
            if is_same_block(
                    text_ann, block,
                    margin_tolerance=margin_tolerance,
                    dif_line_tolerance=dif_line_tolerance,
                    same_line_top_tolerance=same_line_top_tolerance,
                    same_line_tolerance=same_line_tolerance
            ):
                block.update_coord(text_ann)
                column_found = True
                break

        if not column_found:
            blocks.append(TextBlock.from_ann(text_ann))
    return merge_contained_block(blocks)


def get_row_blocks_with_key_value(
        text_anns: List[TextAnn],
        margin_tolerance: float = 0.01,  # phần trăm căn lề trái, phải, giữa
        dif_line_tolerance: float = 0.0075,  # phần trăm khoảng cách giữa 2 hàng
        same_line_top_tolerance: float = 0.005,  # phần trăm độ lệch lề trên để 2 hàng trong 1 dòng
        same_line_tolerance: float = 0.02,  # phần trăm độ lệch để 2 hàng cạnh nhau
        same_key_top_tolerance: float = 0.05,
        same_key_left_tolerance: float = 0.05,
        left_right_key_tolerance: float = 0.2
) -> List[TextBlock]:
    """
    Gom các anns theo vị trí tương đối rất gần nhau ưu tiên item ngang nhau cùng hàng
    """

    line_blocks: List[TextBlock] = []
    mapped_idx = []
    for cur_i, text_ann in enumerate(text_anns):
        if cur_i in mapped_idx:
            continue
        if text_ann.form_tag and text_ann.form_tag.location:
            if text_ann.form_tag.threshold is not None:
                left_right_key_tolerance = text_ann.form_tag.threshold

            match_indices = find_same_line_key_value(
                text_anns, cur_i,
                same_key_top_tolerance=same_key_top_tolerance,
                same_key_left_tolerance=same_key_left_tolerance,
                left_right_key_tolerance=left_right_key_tolerance
            )
            match_indices = [i for i in match_indices if i not in mapped_idx]

            if len(match_indices) > 0:
                if len(match_indices) > 1:
                    match_indices = sorted(match_indices, key=lambda i: abs(text_anns[i].cent_y - text_ann.cent_y))
                match_idx = match_indices[0]
                block = TextBlock.from_ann(text_ann)
                block.mapped_row = True

                nex_ann = text_anns[match_idx]
                block.update_coord(nex_ann)
                mapped_idx.append(match_idx)

                line_blocks.append(block)
                mapped_idx.append(cur_i)

                if text_ann.form_tag.value is None:
                    text_ann.form_tag.value = nex_ann.label
                    nex_ann.is_mapped = True

    blocks: List[TextBlock] = []
    for idx, text_ann in enumerate(text_anns):
        if idx in mapped_idx:
            continue

        column_found = False
        for block in reversed(list(blocks)):
            if is_same_block(
                    text_ann, block,
                    margin_tolerance=margin_tolerance,
                    dif_line_tolerance=dif_line_tolerance,
                    same_line_top_tolerance=same_line_top_tolerance,
                    same_line_tolerance=same_line_tolerance
            ):
                block.update_coord(text_ann)
                column_found = True
                break

        if not column_found:
            blocks.append(TextBlock.from_ann(text_ann))
    blocks.extend(line_blocks)
    return merge_contained_block(blocks)
