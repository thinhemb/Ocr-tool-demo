from pipeline.component.text_order.order_utils.block import get_row_blocks_with_key_value
from pipeline.component.text_order.order_default import DefaultTextOrderComponent
from pipeline.config.key_value_config import KeyValueConfig
from pipeline.data_obj.datapoint import DataPoint


class KeyValueTextOrderComponent(DefaultTextOrderComponent):
    def __init__(
            self, key_value_config: KeyValueConfig = None,
            same_key_top_tolerance: float = 0.05,
            same_key_left_tolerance: float = 0.05,
            left_right_key_tolerance: float = 0.2
    ):
        super().__init__()
        self.key_value_config = key_value_config
        self.same_key_top_tolerance = same_key_top_tolerance
        self.same_key_left_tolerance = same_key_left_tolerance
        self.left_right_key_tolerance = left_right_key_tolerance

    def serve(self, dp: DataPoint) -> None:
        text_anns = dp.text_anns
        for ann in dp.text_anns:
            key_value = self.key_value_config.find_key_value(ann.label)
            ann.form_tag = key_value

        blocks = get_row_blocks_with_key_value(
            text_anns,
            margin_tolerance=self.margin_tolerance,
            dif_line_tolerance=self.dif_line_tolerance,
            same_line_top_tolerance=self.same_line_top_tolerance,
            same_line_tolerance=self.same_line_tolerance,
            same_key_top_tolerance=self.same_key_top_tolerance,
            same_key_left_tolerance=self.same_key_left_tolerance,
            left_right_key_tolerance=self.left_right_key_tolerance,
        )

        # for b in blocks:
        #     print(b)

        sorted_text_anns = self.rearrange_by_reading_blocks_update(blocks)
        dp.text_anns = sorted_text_anns
