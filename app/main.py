from PyQt5.QtWidgets import QApplication
import sys

from Templates.window_main import WindowsTool
import multiprocessing


def main():
    apps = QApplication(sys.argv)
    window = WindowsTool()
    window.show()
    sys.exit(apps.exec_())


if __name__ == "__main__":
    multiprocessing.freeze_support()

    # tool_code = 'Tool_hyouka_consult'
    # StartToolManager(tool_code=tool_code)
    main()
    # print(1)
    # EndToolManager(tool_code=tool_code)
