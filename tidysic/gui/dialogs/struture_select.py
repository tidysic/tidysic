from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from tidysic.gui.widgets import StructureLevelSelect
from tidysic.tag import Tag


class StructureSelect(QDialog):

    def __init__(self, *args, **kwargs):
        super(StructureSelect, self).__init__(*args, **kwargs)

        self.setWindowTitle('Structure definition')

        self.layout = QVBoxLayout(self)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.structure_level_selects = [
            StructureLevelSelect(Tag.Artist, self),
            StructureLevelSelect(Tag.Album, self),
            StructureLevelSelect(None, self),
        ]

        for level in self.structure_level_selects:
            self.layout.addWidget(level)

        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def get_structure(self):
        return list([
            level.value
            for level in self.structure_level_selects
            if level.value is not None
        ])
