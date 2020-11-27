from PyQt5.QtWidgets import QWidget, QHBoxLayout

from tidysic.os_utils import get_audio_files
from tidysic.algorithms import create_structure

from tidysic.gui.widgets import FilesVisualizer, TagsEditor
from tidysic.gui.dialogs import OrderingSelect, FolderSelect


class TreeEditor(QWidget):

    def __init__(self, *args, **kwargs):
        super(TreeEditor, self).__init__(*args, **kwargs)

        layout = QHBoxLayout()
        self.setLayout(layout)

        self.ordering = []
        self.format_strs = []
        self.update_ordering()

        self.visualizer = FilesVisualizer()
        layout.addWidget(self.visualizer)

        self.editor = TagsEditor()
        layout.addWidget(self.editor)

        self.visualizer.itemSelectionChanged.connect(
            self.update_selection
        )

        self.update_structure()

    def update_selection(self):
        selection = self.visualizer.selectedItems()
        self.editor.feed_data([
            item.file
            for item in selection
        ])

    def update_ordering(self):
        ordering_selector = OrderingSelect()
        while not ordering_selector.exec():
            pass

        self.ordering = ordering_selector.get_ordering()
        self.format_strs = ordering_selector.get_format_strs()

    def update_structure(self):
        source_selector = FolderSelect(self, is_input_folder=True)
        while not source_selector.exec():
            pass
        source_dir = source_selector.selectedFiles()[0]
        source = get_audio_files(source_dir)

        root_nodes = create_structure(
            source,
            self.ordering,
            guess=False,
            dry_run=True
        )

        self.visualizer.feed_data(root_nodes, self.format_strs)
