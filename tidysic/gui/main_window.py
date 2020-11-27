from PyQt5.QtWidgets import QMainWindow

from tidysic.gui.widgets import TreeEditor


class TidysicWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(TidysicWindow, self).__init__(*args, **kwargs)

        self._init_layout()
        self._init_menu()

    def _init_layout(self):
        self.tree_editor = TreeEditor()
        self.setCentralWidget(self.tree_editor)

    def _init_menu(self):
        pass
