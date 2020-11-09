from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

# TODO: change into import after merging "arg-as-structure" PR
from collections import namedtuple

StructureLevel = namedtuple(
    'StructureLevel',
    ['ordered', 'unordered']
)


class FilesVisualizer(QTreeWidget):

    def __init__(self, *args, **kwargs):
        super(FilesVisualizer, self).__init__(*args, **kwargs)
        self.setColumnCount(1)

        self.files = StructureLevel([], [])

    def feed_data(self, structure: StructureLevel):
        root = self.create_item(structure)
        self.invisibleRootItem(root)

    def create_item(self, structure: StructureLevel):
        tree_item = QTreeWidgetItem()

        for name, sublevel in structure.ordered:
            if isinstance(sublevel, StructureLevel):
                tree_child_item = self.create_item(sublevel)
                tree_child_item.setText(0, name)

                tree_item.addChild(tree_child_item)
            else:
                # Leaf of the tree
                tree_child_item = QTreeWidgetItem()
                tree_child_item.setText(0, name)

                tree_item.addChild(tree_child_item)

        for file in structure.unordered:
            tree_child_item = QTreeWidgetItem()
            tree_child_item.setText(0, file)

            tree_item.addChild(tree_child_item)

        return tree_item
