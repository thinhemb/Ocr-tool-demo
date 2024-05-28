import copy
import log
from pipeline.base_obj import PipelineComponent
from pipeline.component.text_order.order_utils.block import get_row_blocks
from pipeline.component.text_order.order_utils.col import get_reading_cols, unwind_cols, check_continuous_cols
from pipeline.component.text_order.order_utils.header_footer import get_header_footer
from pipeline.component.text_order.order_utils.row import get_intersect_rows, unwind_rows
from pipeline.component.text_order.order_utils.row_col import get_read_order_dict, rearrange_complex_row_col, \
    rearrange_complex_row_col_update
from pipeline.component.text_order.order_utils.utils import find_intersect_row, get_sorted_anns
from pipeline.data_obj.datapoint import DataPoint


class DefaultTextOrderComponent(PipelineComponent):
    def __init__(self):
        super().__init__()
        self.margin_tolerance: float = 0.01  # phần trăm căn lề trái, phải, giữa
        self.dif_line_tolerance: float = 0.0075  # phần trăm khoảng cách giữa 2 hàng
        self.same_line_top_tolerance: float = 0.005  # phần trăm độ lệch lề trên để 2 hàng trong 1 dòng
        self.same_line_tolerance: float = 0.02  # phần trăm độ lệch để 2 hàng cạnh nhau

        self.top_bot_intersect_tolerance: float = 0.005
        self.left_right_intersect_tolerance: float = 0.01
        self.intersect_per_union_tolerance = 0.1

        self.cent_y_orient_tolerance: float = 0.1  # phần trăm độ lệch giữa 2 vị trí trục y nhỏ hơn thì xếp cùng hàng

        self.left_same_col_tolerance = 0.05
        self.cent_same_col_tolerance = 0.01

    def serve(self, dp: DataPoint) -> None:
        text_anns = dp.text_anns
        blocks = get_row_blocks(
            text_anns,
            margin_tolerance=self.margin_tolerance,
            dif_line_tolerance=self.dif_line_tolerance,
            same_line_top_tolerance=self.same_line_top_tolerance,
            same_line_tolerance=self.same_line_tolerance,
        )

        dp.text_anns = self.rearrange_by_reading_blocks(blocks)

    def rearrange_by_reading_blocks(self, blocks):
        rows = get_intersect_rows(
            blocks,
            top_bot_intersect_tolerance=self.top_bot_intersect_tolerance,
            intersect_per_union_tolerance=self.intersect_per_union_tolerance
        )
        rows = unwind_rows(rows)

        if all([len(r) == 1 for r in rows]):
            order_blocks = [r[0] for r in rows]
            return get_sorted_anns(order_blocks)

        col_sorted_text_anns = self.rearrange_by_col(blocks)
        if col_sorted_text_anns is not None:
            return get_sorted_anns(col_sorted_text_anns)

        order_blocks = rearrange_complex_row_col(rows)
        return get_sorted_anns(order_blocks)

    def rearrange_by_reading_blocks_update(self, blocks):
        rows = get_intersect_rows(
            blocks,
            top_bot_intersect_tolerance=self.top_bot_intersect_tolerance,
            intersect_per_union_tolerance=self.intersect_per_union_tolerance
        )
        rows = unwind_rows(rows)

        if all([len(r) == 1 for r in rows]):
            order_blocks = [r[0] for r in rows]
            return get_sorted_anns(order_blocks)

        col_sorted_text_anns = self.rearrange_by_col(blocks)
        if col_sorted_text_anns is not None:
            return get_sorted_anns(col_sorted_text_anns)

        order_blocks = rearrange_complex_row_col_update(rows)
        return get_sorted_anns(order_blocks)

    def rearrange_by_col(self, blocks):
        col_blocks = copy.deepcopy(blocks)
        cols = get_reading_cols(
            col_blocks,
            left_same_col_tolerance=self.left_same_col_tolerance,
            cent_same_col_tolerance=self.cent_same_col_tolerance
        )
        if len(cols) >= 2:
            cols = unwind_cols(cols)

        if len(cols) == 2:
            if check_continuous_cols(cols):
                log.dlog_d("Page contains only 2 cols")
                return get_read_order_dict(cols)

            temp_cols = copy.deepcopy(cols)
            header_row, body_cols, footer_row = get_header_footer(temp_cols)

            if body_cols is not None:
                log.dlog_d("Page contains 2 cols without header and footer")
                return get_read_order_dict(body_cols, header_row, footer_row)

        elif len(cols) == 3:
            for i in range(2):
                if all([find_intersect_row(r, cols[i], intersect_tolerance=0.001) is None for r in cols[i + 1]]):
                    temp_cols = copy.deepcopy(cols)
                    temp_cols[i].extend(temp_cols[i + 1])
                    temp_cols.pop(i + 1)

                    if check_continuous_cols(temp_cols):
                        log.dlog_d("Page contains 3 cols without table")
                        return get_read_order_dict(temp_cols)

                    header_row, body_cols, footer_row = get_header_footer(temp_cols)

                    if body_cols is not None:
                        log.dlog_d("Page contains 3 cols with header and footer")
                        return get_read_order_dict(body_cols, header_row, footer_row)
                    break
        return None

    def health_check(self) -> bool:
        return True
