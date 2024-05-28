from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog
# from PyQt5 import uic
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot, QThread
import os

from Templates.WindowMain import Ui_MainWindow
from extract_info import ExtractInfo

IMAGE_EXTENSIONS = [
    '.jpg', '.png', '.jpeg', '.tif', '.tiff', '.bmp', '.jpe', '.jpeg', '.jp2', '.webp',
    '.pbm', '.pgm', '.ppm', '.pxm', '.pnm', '.sr', '.ras', '.hdr', '.pic', '.exr'
]


class WindowsTool(QMainWindow):
    def __init__(self):
        super().__init__()

        # self.ui = uic.loadUi(r"Templates\WindowMain_.ui", self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.envs = {}

        self._input_folder_images = self.findChild(QtWidgets.QLineEdit, "input_folder_images")
        self._input_file_summary = self.findChild(QtWidgets.QLineEdit, "input_file_summary")

        self._button_folder_images = self.findChild(QtWidgets.QPushButton, "button_folder_images")
        self._button_folder_images.clicked.connect(lambda: self.on_button_folder_images_clicked)

        self._button_file_summary = self.findChild(QtWidgets.QPushButton, "button_file_summary")
        self._button_file_summary.clicked.connect(lambda: self.on_button_file_summary_clicked)

        self._button_cancel = self.findChild(QtWidgets.QPushButton, "button_cancel")
        self._button_cancel.clicked.connect(self.close)

        self._button_extract = self.findChild(QtWidgets.QPushButton, "button_extract")
        self._button_extract.clicked.connect(lambda: self.on_button_extract_clicked)

        self._comboBox_lang = self.findChild(QtWidgets.QComboBox, "comboBox_lang")

        self._button_reset = self.findChild(QtWidgets.QPushButton, "button_reset")
        self._button_reset.clicked.connect(lambda: self.on_button_reset_clicked)

        self.path_save = None
        self.extractor = None
        self.thread = None
        # self.set_default_input()
        self.closeEvent = self.closeEvent

    @pyqtSlot()
    def on_button_reset_clicked(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Notification")
        msg_box.setText("<font color = red >Do you want to reset input? </font >")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("background-color: rgb(240, 240, 240);")
        ret = msg_box.exec()

        if ret == QMessageBox.Yes:
            self._input_folder_images.setText('')
            self._input_file_summary.setText('')

    # def set_default_input(self):
    #     folder_path = r"C:\Users\KNT21818\Documents\WorkSpace\Tool_hyouka_consult_v2.0\data\japan"
    #     file_path = r"C:\Users\KNT21818\Documents\WorkSpace\Tool_hyouka_consult_v2.0\data\temp\F_【AEMS_step1】C3P_CS_Master_.xlsm"
    #     self._input_folder_images.setText(folder_path)
    #     self._input_file_summary.setText(file_path)

    @staticmethod
    def show_message_box(status, text):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(status)
        msg_box.setText(text)
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    @pyqtSlot()
    def on_button_folder_images_clicked(self):
        folder_path = QFileDialog.getExistingDirectory(self, 'Choose folder')
        self._input_folder_images.setText(folder_path)

    @pyqtSlot()
    def on_button_file_summary_clicked(self):
        folder = QFileDialog.getOpenFileName(None, 'Choose file summary', filter='*.xlsm')[0]
        self._input_file_summary.setText(folder)

    def check_flag_file_summary(self):
        file_summary_text = self._input_file_summary.text().strip()
        check_file_summary = self.check_info_file_summary(file_summary_text)
        if check_file_summary > 0:
            self.envs["file_summary"] = file_summary_text
            return True
        else:
            text = "File summary isn't file 'xlsm'. Please select again!"
        status = "Error"
        self.show_message_box(status, text)
        return False

    def check_flag_folder_images(self):
        folder_images_text = self._input_folder_images.text().strip()
        check_ = self.check_info(folder_images_text, check_img=True)
        if check_:
            self.envs["folder_images"] = folder_images_text
            return True
        else:
            text = "Folder images does not contain images \nor Folder images is not exist! \
             \nPlease select folder in folder images again!"
        status = "Error"
        self.show_message_box(status, text)
        return False

    @pyqtSlot()
    def on_button_extract_clicked(self):

        check_ = self.check_flag_folder_images()
        if check_:
            check_file_summary = self.check_flag_file_summary()
            if check_file_summary:
                self.setEnabled(False)
                self._button_extract.setText("Tool is running")
                self.envs["lang"] = self._comboBox_lang.currentText().lower()
                if self.envs["lang"] == 'english':
                    self.envs["lang"] = 'en'
                self.extractor = ExtractInfo(self.envs)
                self.thread = QThread()
                self.extractor.moveToThread(self.thread)
                self.thread.started.connect(self.extractor.run)
                self.extractor.finished.connect(self.thread.quit)
                self.extractor.finished.connect(self.extractor.deleteLater)
                self.thread.finished.connect(self.thread.deleteLater)
                self.thread.start()
                self.thread.finished.connect(lambda: self.thread_finish())
        return None

    def thread_finish(self):
        self.path_save = self.extractor.get_path_save()
        self.setEnabled(True)
        self._button_extract.setText("Run")
        text = f"Finished!\nExtract information is saved in file:\n{self.path_save}"
        status = "Notification"
        self.show_message_box(status, text)

    def closeEvent(self, event):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Notification")
        msg_box.setText("<font color = red >Are you sure you want to exit? </font >")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("background-color: rgb(240, 240, 240);")

        ret = msg_box.exec()

        if ret == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    @staticmethod
    def check_info(folder_path, check_img=False):
        if not os.path.exists(folder_path):
            return False
        else:
            if check_img:
                image_files = [f for f in os.listdir(folder_path) if
                               os.path.isfile(os.path.join(folder_path, f))]  # Các phần mở rộng ảnh hợp lệ
                for file in image_files:
                    _, file_extension = os.path.splitext(file)
                    if file_extension.lower() in IMAGE_EXTENSIONS:
                        return True
                return False
            else:
                return True

    @staticmethod
    def check_info_file_summary(path):
        if os.path.exists(path) and '.xlsm' in path and '~$' not in path:
            return True
        return False
