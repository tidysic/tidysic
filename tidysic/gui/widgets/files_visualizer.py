from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from tidysic.algorithms import StructureLevel
from tidysic.audio_file import AudioFile


class FileTreeItem(QTreeWidgetItem):

    def __init__(self, file: AudioFile, format: str, *args, **kwargs):
        super(FileTreeItem, self).__init__(*args, **kwargs)
        self.setText(
            0,
            file.build_file_name(format)
        )

        self.file = file


class FilesVisualizer(QTreeWidget):

    def __init__(self, format, *args, **kwargs):
        super(FilesVisualizer, self).__init__(*args, **kwargs)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

        # TODO: Find a way to to multi-file tag editing
        self.setSelectionMode(QAbstractItemView.SingleSelection)

        self.format = format

    def feed_data(self, structure: StructureLevel):
        root: QTreeWidgetItem = self.create_item(structure)

        items = root.takeChildren()
        self.addTopLevelItems(sorted(
            items,
            key=lambda item: item.text(0).lower()
        ))

    def create_item(self, structure: StructureLevel):
        tree_item = QTreeWidgetItem()

        for name, sublevel in structure.ordered.items():
            if isinstance(sublevel, StructureLevel):
                tree_child_item = self.create_item(sublevel)
                tree_child_item.setText(0, name)

                tree_item.addChild(tree_child_item)
            else:
                # Leaf of the tree
                tree_child_item = QTreeWidgetItem()
                tree_child_item.setText(0, name)
                for file in sublevel:
                    tree_leaf_item = FileTreeItem(file, self.format)
                    tree_child_item.addChild(tree_leaf_item)

                tree_item.addChild(tree_child_item)

        for file in structure.unordered:
            tree_child_item = FileTreeItem(file, self.format)
            tree_item.addChild(tree_child_item)

        return tree_item
