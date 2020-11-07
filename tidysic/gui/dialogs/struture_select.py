from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout


class StructureSelect(QDialog):

    def __init__(self, *args, **kwargs):
        super(StructureSelect, self).__init__(*args, **kwargs)

        self.setWindowTitle('Structure definition')
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )

        self.structure_level_selects = [
            
        ]

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)
