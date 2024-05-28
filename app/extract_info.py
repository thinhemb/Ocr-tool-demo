import os
from pathlib import Path
import pandas as pd
import time
from PyQt5.QtCore import QObject, pyqtSignal
import xlwings as xw

import log
from pipeline.component.pre import IMAGE_EXTENSIONS
from pipeline.pipeline import Pipeline
import dconfig


class ExtractInfo(QObject):
    finished = pyqtSignal()

    def __init__(self, envs):
        super(ExtractInfo, self).__init__()
        self.path_save = None
        self.envs = envs
        self.list_images = []
        self.results = []
        self.pipeline = self.load_pipeline()
        # self.list_text = []

    def load_pipeline(self):
        pipeline = Pipeline.build(model_config=dconfig.model_config, lang=self.envs['lang'])
        return pipeline

    def get_file_images(self):
        list_images = []
        for file in os.listdir(self.envs["folder_images"]):
            if isinstance(file, str):
                path = Path(os.path.join(self.envs["folder_images"], file))
                suffix = path.suffix.lower()
                if suffix in IMAGE_EXTENSIONS:
                    list_images.append(path)
        return list_images

    def save_file(self):
        # print(self.results)
        self.create_path_excel()
        # print(self.path_save)
        path_img = []
        signals = []
        values = []
        status_logs = []
        for res in self.results:
            for item in res.list_signals_values:
                path_img.append(res.name_image)
                signals.append(item["signal"])
                values.append(item["value"])
                if item["status_log"]:
                    key = "まとめファイルに信号名が見つかって、値を記入した"
                else:
                    key = "まとめファイルに信号名が見つからない"
                status_logs.append(key)
        df = pd.DataFrame({
            "Path image": path_img,
            "Signals": signals,
            "Values": values,
            "Status logs": status_logs
        })
        df.to_excel(self.path_save, index=False)

    def create_path_excel(self):
        now = time.localtime()
        paths = "\\".join(os.getcwd().split('\\')[:-1])
        path_folder = os.path.join(paths, 'data\\temp')
        if not os.path.exists(path_folder):
            os.makedirs(path_folder)
        # Định dạng ngày tháng năm giờ phút theo định dạng mong muốn
        date_format = time.strftime("%Y-%m-%d_%H-%M-%S", now)
        file_name = "extract_info_" + date_format + ".xlsx"
        self.path_save = os.path.join(path_folder, file_name)

    def get_path_save(self):
        return self.path_save

    def run(self):
        self.path_save = None
        self.results = []
        self.list_images = self.get_file_images()
        for path in self.list_images:
            result = self.pipeline.analyze(path=path, lang=self.envs['lang'])
            self.results.append(result)
        # start = time.perf_counter()
        self.edit_summary()
        # print(time.perf_counter()-start)
        self.save_file()
        # df = pd.DataFrame({
        #     "Data": self.list_text
        # })
        # df.to_excel(r'C:\Users\KNT21818\Documents\WorkSpace\Tool_hyouka_consult_v1\app\data\config\list_signal.xlsx',
        #             index=False)
        self.finished.emit()

    def edit_summary(self):
        # pass
        excel_app = xw.App(visible=False)

        wb = excel_app.books.open(self.envs["file_summary"])
        #
        for sheet in wb.sheets:
            if "$22" in sheet.name:
                self.process_data(sheet)
        wb.save()
        wb.close()
        # break
        excel_app.quit()

    @staticmethod
    def find_key_col(sheet, key, row_start=3, col_start=7):
        for row in range(row_start, 6):
            for col in range(col_start, 17):
                if sheet.range((row, col)).value == key:
                    return row, col
        return -1, -1

    def process_data(self, sheet):
        # tìm vị trí ô chứa "C3P Display Name'
        row_index_signal, column_index_signal = self.find_key_col(sheet, "C3P Display Name")
        row_index_value, column_index_value = self.find_key_col(sheet, "C3P Value", row_index_signal,
                                                                column_index_signal)
        if column_index_value > 0 and column_index_signal > 0:
            # print(sheet.name)
            count_row = sheet.range((row_index_signal, column_index_signal)).end('down').row
            list_signal_in_file_summary = [sheet.cells(i, column_index_signal).value
                                           for i in range(row_index_signal, count_row)]
            for index_res in range(len(self.results)):

                for index_signal in range(len(self.results[index_res].list_signals_values)):
                    signal = self.results[index_res].list_signals_values[index_signal]['signal']
                    if (signal not in list_signal_in_file_summary or
                            self.results[index_res].list_signals_values[index_signal]['value'] is None):
                        continue
                    for index in range(row_index_signal, count_row + 1):
                        # if sheet.range((index, column_index_signal)).value == '(TBD)Engine inlet coolant temperature':
                        # if sheet.range((index, column_index_signal)).value not in self.list_text:
                        #     self.list_text.append(sheet.range((index, column_index_signal)).value)
                        try:
                            if sheet.range((index, column_index_signal)).value == signal:
                                # value = sheet.range((index, column_index_value)).value
                                sheet.range((index, column_index_value)).value = \
                                    self.results[index_res].list_signals_values[index_signal]['value']
                                self.results[index_res].list_signals_values[index_signal]['status_log'] = True
                                break
                        except Exception as e:
                            log.dlog_e(f'Error: {e}')
                            continue
        return sheet

# if __name__ == '__main__':
#     ex = ExtractInfo()
#     envs = {'folder_images': r"C:\Users\KNT21818\Documents\WorkSpace\Tool_hyouka_consult_v1\data\temp",
#             "folder_save": r"C:\Users\KNT21818\Documents\WorkSpace\Tool_hyouka_consult_v1\data\results"}
#     path_save = ex.run(envs)
#     print(path_save)
