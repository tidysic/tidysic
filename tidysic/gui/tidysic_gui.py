from PyQt5 import QtWidgets

from .. import parse_in_directory, log
from .dialogs import FolderSelect, StructureSelect


def run():

    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()

    input_dialog = FolderSelectDialog(window, True)

    if input_dialog.exec():
        input_dir = input_dialog.selectedFiles()[0]

        artists = parse_in_directory(input_dir, True, False)

        # Debug
        message = []
        for artist, albums in artists.items():
            message.append(f'Artist : {artist}')
            for album, titles in albums.items():
                message.append(f'\tAlbum : {album}')
                for title in titles.items():
                    message.append(f'\t\tTitle : {title}')
        log(message)

    window.show()
    app.exec()


if __name__ == '__main__':

    run()
