from pathlib import Path
from tidysic.file.taggable import Taggable

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from tidysic.file.clutter_file import ClutterFile


class AudioFile(Taggable):
    """Parsed audio file with mutagene, for easily accessing its tags."""

    extensions = {
        '.flac',
        '.mp3',
        '.ogg',
        '.wav',
    }

    def __init__(self, path: Path):
        self.path = path
        self.extension: str = self.path.suffix

        self._parse()

    def _parse(self) -> None:
        tags = self._get_mutagen_tags()
        self.set_tags(tags)

    def _get_mutagen_tags(self) -> dict:
        try:
            return {
                k: v[0]
                for k, v in EasyID3(self.path.resolve()).items()
            }
        except ID3NoHeaderError:
            return dict()

    def get_title_with_extension(self) -> str:
        return self.title + self.extension

    @staticmethod
    def is_audio_file(path: Path) -> bool:
        return path.is_file() and path.suffix in AudioFile.extensions

    def __hash__(self) -> int:
        return hash(self.path)