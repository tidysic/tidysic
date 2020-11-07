from PyQt5.QtWidgets import QComboBox

from tidysic.tag import Tag


class StructureLevelSelect(QComboBox):

    def __init__(self, value: Tag, *args, **kwargs):
        super(StructureLevelSelect, self).__init__(*args, **kwargs)

        self.setInsertPolicy(QComboBox.NoInsert)

        self.value = value

        self.addItem("None")
        for i, tag in enumerate(Tag, 1):
            self.addItem(str(tag))
            if tag == value:
                self.setCurrentIndex(i)

    def currentIndexChanged(self, index):
        if self.currentText == "None":
            self.value = None
        else:
            for tag in Tag:
                if self.currentText == str(tag):
                    self.value = tag
