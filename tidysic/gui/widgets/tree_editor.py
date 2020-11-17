from PyQt5.QtWidgets import QWidget, QHBoxLayout

from tidysic.gui.widgets import FilesVisualizer, TagsEditor


class TreeEditor(QWidget):

    def __init__(self, format, *args, **kwargs):
        super(TreeEditor, self).__init__(*args, **kwargs)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.visualizer = FilesVisualizer(format)
        layout.addWidget(self.visualizer)

        self.editor = TagsEditor()
        layout.addWidget(self.editor)

        # TODO: Connect
