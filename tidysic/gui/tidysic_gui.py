from PyQt5 import QtWidgets

from tidysic import create_structure, move_files, clean_up
from tidysic.os_utils import get_audio_files
from tidysic.gui.dialogs import FolderSelect, OrderingSelect


def run():

    _ = QtWidgets.QApplication([])

    in_directory_selector = FolderSelect(None, is_input_folder=True)
    while not in_directory_selector.exec():
        pass
    source_dir = in_directory_selector.selectedFiles()[0]

    out_directory_selector = FolderSelect(None, is_input_folder=False)
    while not out_directory_selector.exec():
        pass
    target_dir = out_directory_selector.selectedFiles()[0]

    ordering_select = OrderingSelect(None)
    while not ordering_select.exec():
        pass
    ordering = ordering_select.get_ordering()

    # TODO: Create dialog for format specification
    format = '{title}'

    source_files = get_audio_files(source_dir)

    root = create_structure(
        source_files,
        ordering,
        guess=False,
        dry_run=True
    )

    move_files(
        root,
        target_dir,
        format,
        dry_run=True
    )

    clean_up(
        source_dir,
        source_files,
        dry_run=True
    )

    # app.exec()


if __name__ == '__main__':

    run()
