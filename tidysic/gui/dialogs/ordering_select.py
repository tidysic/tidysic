from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from tidysic.gui.widgets import OrderingLevelSelect
from tidysic.tag import Tag


class OrderingSelect(QDialog):

    def __init__(self, *args, **kwargs):
        super(OrderingSelect, self).__init__(*args, **kwargs)

        self.setWindowTitle('Structure definition')

        self.layout = QVBoxLayout(self)
        self.sublayout = QVBoxLayout()
        self.setLayout(self.layout)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layout.addLayout(self.sublayout)
        self.layout.addWidget(self.button_box)

        self.ordering_level_selects = [
            OrderingLevelSelect(Tag.Artist, self),
            OrderingLevelSelect(Tag.Album, self),
            OrderingLevelSelect(None, self),
        ]

        self.onOrderingLevelsChanged()

    def get_ordering(self):
        return list([
            level.value
            for level in self.ordering_level_selects
            if level.value is not None
        ])

    def onOrderingLevelsChanged(self):

        ordering = self.get_ordering()

        # Filter out the Nones
        ordering = list([
            tag
            for tag in ordering
            if tag is not None
        ])

        # Clear the layout
        for level_select in self.ordering_level_selects:
            self.sublayout.removeWidget(level_select)
            level_select.deleteLater()

        # Recreate selects, with a None at the end
        self.ordering_level_selects = list([
            OrderingLevelSelect(tag, self)
            for tag in ordering + [None]
        ])

        # Fill the layout
        for level in self.ordering_level_selects:
            self.sublayout.addWidget(level)
