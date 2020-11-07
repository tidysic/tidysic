from PyQt5 import QtWidgets

from tidysic import organise, log
from tidysic.tag import Tag
from tidysic.gui.dialogs import FolderSelect, StructureSelect


def run():

    app = QtWidgets.QApplication([])

    in_directory_selector = FolderSelect(None, is_input_folder=True)
    while not in_directory_selector.exec():
        pass
    source = in_directory_selector.selectedFiles()[0]

    out_directory_selector = FolderSelect(None, is_input_folder=False)
    while not out_directory_selector.exec():
        pass
    target = out_directory_selector.selectedFiles()[0]

    structure_select = StructureSelect(None)
    while not structure_select.exec():
        pass
    structure = structure_select.get_structure() + [Tag.Title]

    log("sauce")
    
    organise(
        source,
        target,
        with_album=True,
        guess=False,
        dry_run=True,
        verbose=True
    )

    log("sauce")

    # app.exec()


if __name__ == '__main__':

    run()
