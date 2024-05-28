def validate_block_size(block, width, height):
    bbox = list(block['bbox'])
    if any([cor < 0 for cor in bbox]):
        return True
    if bbox[0] > 1.5 * width or \
            bbox[2] > 1.5 * width or \
            bbox[1] > 1.5 * height or \
            bbox[3] > 1.5 * height:
        return True

    if bbox[0] > width or \
            bbox[2] > width or \
            bbox[1] > height or \
            bbox[3] > height:
        if bbox[0] > width:
            bbox[0] = width
        if bbox[2] > width:
            bbox[2] = width
        if bbox[1] > height:
            bbox[1] = height
        if bbox[3] > height:
            bbox[3] = height
        block['bbox'] = tuple(bbox)
    return False


def join_block_str(block):
    return "".join(["".join([s["text"] for s in line["spans"]]) for line in block['lines']]).strip()


def check_page_has_text(page_obj):
    blocks = page_obj['blocks']
    width = page_obj['width']
    height = page_obj['height']
    valid_blocks = [block for block in blocks if
                    block['type'] == 0 and not validate_block_size(block, width, height)
                    and join_block_str(block) != ""]
    if len(valid_blocks) <= 2:
        return False
    if len(valid_blocks) / len(blocks) < 0.05:
        return False
    text = "".join([join_block_str(block) for block in valid_blocks])
    if text.strip() == "":
        return False
    return True
