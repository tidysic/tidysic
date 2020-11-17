from PyQt5.QtWidgets import (
    QMainWindow,
    QHBoxLayout
)

from tidysic.gui.widgets import (
    OrderingLevelSelect,
    TreeEditor
)
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

        self.tree_editor = TreeEditor(self.format)
        self.setCentralWidget(self.tree_editor)
