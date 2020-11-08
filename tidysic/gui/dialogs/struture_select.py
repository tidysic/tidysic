from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout

from tidysic.gui.widgets import StructureLevelSelect
from tidysic.tag import Tag


class StructureSelect(QDialog):

    def __init__(self, *args, **kwargs):
        super(StructureSelect, self).__init__(*args, **kwargs)

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

        self.structure_level_selects = [
            StructureLevelSelect(Tag.Artist, self),
            StructureLevelSelect(Tag.Album, self),
            StructureLevelSelect(None, self),
        ]

        self.onStructureLevelsChanged()

    def get_structure(self):
        return list([
            level.value
            for level in self.structure_level_selects
            if level.value is not None
        ])

    def onStructureLevelsChanged(self):

        # Filter out the Nones
        structure = self.get_structure()
        structure = list([
            tag
            for tag in structure
            if tag is not None
        ])

        # Clear the layout
        for level_select in self.structure_level_selects:
            self.sublayout.removeWidget(level_select)
            level_select.deleteLater()

        # Recreate selects, with a None at the end
        self.structure_level_selects = list([
            StructureLevelSelect(tag, self)
            for tag in structure + [None]
        ])

        # Fill the layout
        for level in self.structure_level_selects:
            self.sublayout.addWidget(level)
