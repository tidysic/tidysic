from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QComboBox,
    QLineEdit
)

from PyQt5.QtCore import pyqtSignal

from tidysic.tag import Tag


class OrderingLevelSelect(QWidget):

    changed = pyqtSignal()

    def __init__(self, value: Tag, parent, *args, **kwargs):
        super(OrderingLevelSelect, self).__init__(parent, *args, **kwargs)

        self.value = value

        layout = QHBoxLayout(self)
        self.setLayout(layout)

        self.combo = QComboBox(self)
        layout.addWidget(self.combo)
        self.combo.setInsertPolicy(QComboBox.NoInsert)
        self.combo.addItem("None")
        for i, tag in enumerate(Tag, 1):
            self.combo.addItem(str(tag))
            if tag == value:
                self.combo.setCurrentIndex(i)

        self.combo.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.changed.connect(parent.onOrderingLevelsChanged)

        self.format_edit = QLineEdit(self)
        layout.addWidget(self.format_edit)
        self._update_format_field()

    def onCurrentIndexChanged(self, index):
        new_text = self.combo.currentText()
        if new_text == "None":
            self.value = None
        else:
            for tag in Tag:
                if new_text == str(tag):
                    self.value = tag

        self.changed.emit()

    def _update_format_field(self):
        if self.value is None:
            self.format_edit.setText('{{track:02d}. }{{title}}')
        elif self.value == Tag.Album:
            self.format_edit.setText('{({year}) }{{album}}')
        else:
            self.format_edit.setText(
                f'{{{{{str(self.value).lower()}}}}}'
            )
