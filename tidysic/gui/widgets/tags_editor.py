from PyQt5.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QComboBox
)

from tidysic.tag import Tag
from tidysic.audio_file import AudioFile


class TagsEditor(QWidget):

    def __init__(self, *args, **kwargs):
        super(TagsEditor, self).__init__(*args, **kwargs)
        self.fields = {}
        self.create_layout()

    def create_layout(self):
        layout = QFormLayout(self)
        self.setLayout(layout)

        self.fields[Tag.Track] = QSpinBox(self)
        layout.addRow(
            self.tr('Trac&k'),
            self.fields[Tag.Track]
        )

        self.fields[Tag.Title] = QLineEdit(self)
        layout.addRow(
            self.tr('&Title'),
            self.fields[Tag.Title]
        )

        self.fields[Tag.Artist] = QLineEdit(self)
        layout.addRow(
            self.tr('&Artist'),
            self.fields[Tag.Artist]
        )

        self.fields[Tag.Album] = QLineEdit(self)
        layout.addRow(
            self.tr('Al&bum'),
            self.fields[Tag.Album]
        )

        self.fields[Tag.Year] = QSpinBox(self)
        layout.addRow(
            self.tr('&Year'),
            self.fields[Tag.Year]
        )

        self.fields[Tag.Genre] = QComboBox(self)
        self.fields[Tag.Genre].setEditable(False)
        self.fields[Tag.Genre].addItems([
            'Techno',
            'Classical'
        ])  # TODO: Create items from actual genres enum
        layout.addRow(
            self.tr('&Genre'),
            self.fields[Tag.Genre]
        )

    def feed_data(self, file: AudioFile):
        for tag in Tag:
            value = file.tags[tag]
            field = self.fields[tag]
            if value is None:
                field.clear()

            else:
                if isinstance(field, QLineEdit):
                    if value:
                        field.setText(value)

                elif isinstance(field, QSpinBox):
                    if value:
                        field.setValue(value)

                elif isinstance(field, QComboBox):
                    if value:
                        found_index = field.findText(value)
                        if found_index >= 0:
                            field.setCurrentIndex(found_index)
                        else:
                            # TODO: Check if this is a good thing to do
                            # Genre tags may actually be just an enum
                            field.addItem(value)
