from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import pyqtSignal

from tidysic.tag import Tag


class OrderingLevelSelect(QComboBox):

    changed = pyqtSignal()

    def __init__(self, value: Tag, parent, *args, **kwargs):
        super(OrderingLevelSelect, self).__init__(parent, *args, **kwargs)

        self.setInsertPolicy(QComboBox.NoInsert)

        self.value = value

        self.addItem("None")
        for i, tag in enumerate(Tag, 1):
            self.addItem(str(tag))
            if tag == value:
                self.setCurrentIndex(i)

        self.currentIndexChanged.connect(self.onCurrentIndexChanged)
        self.changed.connect(parent.onOrderingLevelsChanged)

    def onCurrentIndexChanged(self, index):
        new_text = self.currentText()
        if new_text == "None":
            self.value = None
        else:
            for tag in Tag:
                if new_text == str(tag):
                    self.value = tag

        self.changed.emit()
