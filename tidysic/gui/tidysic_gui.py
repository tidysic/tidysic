from PyQt5 import QtWidgets

from tidysic import Tag, create_structure

from .folder_select_dialog import FolderSelectDialog


def run():

    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()

    input_dialog = FolderSelectDialog(window, True)

    if input_dialog.exec():
        input_dir = input_dialog.selectedFiles()[0]
        ordering = [Tag.Artist, Tag.Album]

        artists = create_structure(input_dir, ordering, False, True)  # noqa

    window.show()
    app.exec()


if __name__ == '__main__':

    run()
