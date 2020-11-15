from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from tidysic.algorithms import StructureLevel


class FilesVisualizer(QTreeWidget):

    def __init__(self, format, *args, **kwargs):
        super(FilesVisualizer, self).__init__(*args, **kwargs)
        self.setColumnCount(1)
        self.format = format

    def feed_data(self, structure: StructureLevel):
        root: QTreeWidgetItem = self.create_item(structure)

        items = root.takeChildren()
        self.addTopLevelItems(items)

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
                for song in sublevel:
                    song_name = song.build_file_name('{title}')
                    tree_leaf_item = QTreeWidgetItem()
                    tree_leaf_item.setText(0, song_name)

                    tree_child_item.addChild(tree_leaf_item)

                tree_item.addChild(tree_child_item)

        for file in structure.unordered:
            tree_child_item = QTreeWidgetItem()
            tree_child_item.setText(0, file)

            tree_item.addChild(tree_child_item)

        return tree_item
