from PyQt5.QtWidgets import QMainWindow

from tidysic.os_utils import get_audio_files
from tidysic.algorithms import create_structure

from tidysic.gui.widgets import TreeEditor
from tidysic.gui.dialogs import (
    FolderSelect,
    OrderingSelect
)


class TidysicWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TidysicWindow, self).__init__(*args, **kwargs)

        self.files = []
        self.tree = {}
        self.format = '{title}'

        self._init_layout()

        self._init_menu()

        source_selector = FolderSelect(self, is_input_folder=True)
        while not source_selector.exec():
            pass
        source_dir = source_selector.selectedFiles()[0]

        source = get_audio_files(source_dir)

        ordering_selector = OrderingSelect()
        while not ordering_selector.exec():
            pass
        ordering = ordering_selector.get_ordering()

        root = create_structure(
            source,
            ordering,
            guess=False,
            dry_run=True
        )

        self.tree_editor.visualizer.feed_data(root)

    def _init_layout(self):
        self.tree_editor = TreeEditor(self.format)
        self.setCentralWidget(self.tree_editor)

    def _init_menu(self):
        pass
