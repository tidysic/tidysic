from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView

from tidysic.algorithms import TreeNode
from tidysic.audio_file import AudioFile


class FileTreeItem(QTreeWidgetItem):

    def __init__(self, file: AudioFile, format_str: str, *args, **kwargs):
        super(FileTreeItem, self).__init__(*args, **kwargs)
        self.setText(
            0,
            file.fill_formatted_str(format_str)
        )

        self.file = file


class FilesVisualizer(QTreeWidget):

    def __init__(self, *args, **kwargs):
        super(FilesVisualizer, self).__init__(*args, **kwargs)
        self.setColumnCount(1)
        self.setHeaderHidden(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def feed_data(
        self,
        root_nodes: list,
        format_strs: list
    ):
        items = [
            self.create_item(node, format_strs)
            for node in root_nodes
        ]
        self.addTopLevelItems(sorted(
            items,
            key=lambda item: item.text(0).lower()
        ))

    def create_item(
        self,
        node,
        format_strs
    ):
        if not format_strs:
            format_strs = self.format_strs

        if isinstance(node, TreeNode):

            tree_item = QTreeWidgetItem()
            tree_item.setText(0, node.build_name(format_strs[0]))

            children = [
                self.create_item(child, format_strs[1:])
                for child in node.children
            ]
            children.sort(key=lambda node: node.text(0))
            tree_item.addChildren(children)
            return tree_item

        else:
            return FileTreeItem(node, format_strs[0])
