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

        track_edit = QSpinBox(self)
        layout.addRow(
            self.tr('Trac&k'),
            track_edit
        )
        self.fields[Tag.Track] = track_edit

        title_edit = QLineEdit(self)
        layout.addRow(
            self.tr('&Title'),
            title_edit
        )
        self.fields[Tag.Title] = title_edit

        artist_edit = QLineEdit(self)
        layout.addRow(
            self.tr('&Artist'),
            artist_edit
        )
        self.fields[Tag.Artist] = artist_edit

        album_edit = QLineEdit(self)
        layout.addRow(
            self.tr('Al&bum'),
            album_edit
        )
        self.fields[Tag.Album] = album_edit

        year_edit = QSpinBox(self)
        year_edit.setMaximum(3000)  # No one will use this program by then
        layout.addRow(
            self.tr('&Year'),
            year_edit
        )
        self.fields[Tag.Year] = year_edit

        genre_edit = QComboBox(self)
        genre_edit.setEditable(False)
        genre_edit.addItems([
            'Techno',
            'Classical'
        ])  # TODO: Create items from actual genres enum
        layout.addRow(
            self.tr('&Genre'),
            genre_edit
        )
        self.fields[Tag.Genre] = genre_edit

    def feed_data(self, file: AudioFile):  # ClutterFiles should work too here
        from tidysic import logger
        logger.warning(str(file.tags))
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
                        field.setValue(int(value))

                elif isinstance(field, QComboBox):
                    if value:
                        found_index = field.findText(value)
                        if found_index >= 0:
                            field.setCurrentIndex(found_index)
                        else:
                            # TODO: Check if this is a good thing to do
                            # Genre tags may actually be just an enum
                            field.addItem(value)
