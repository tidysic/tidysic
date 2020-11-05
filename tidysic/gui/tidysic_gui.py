# import tidysic

from PyQt5 import QtWidgets

from .. import parse_in_directory, log

from .folder_select_dialog import FolderSelectDialog


def run():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()

    input_dialog = FolderSelectDialog(window, True)

    if input_dialog.exec():
        input_dirs = input_dialog.selectedFiles()
        log(input_dirs)

    window.show()
    app.exec()


if __name__ == "__main__":

    run()
