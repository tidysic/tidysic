from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


class AudioFile:
    """Parsed audio file with mutagene, for easily accessing its tags."""

    extensions = {
        '.flac',
        '.mp3',
        '.ogg',
        '.wav',
    }

    def __init__(self, path: Path) -> None:
        self.path = path

        self.album: str = 'Unknown'
        self.artist: str = 'Unknown'
        self.title: str = path.stem
        self.genre: str = 'Unknown'
        self.tracknumber: str = 'Unknown'
        self.date: str = 'Unknown'
        self.extension: str = self.path.suffix

        self._parse()

    def _parse(self) -> None:
        tags = self._get_mutagen_tags()
        for k, v in tags.items():
            setattr(self, k, v[0])

    def _get_mutagen_tags(self) -> dict:
        try:
            return dict(EasyID3(self.path.resolve()))
        except ID3NoHeaderError:
            return dict()

    def get_title_with_extension(self) -> str:
        return self.title + self.extension

    @staticmethod
    def is_audio_file(path: Path) -> bool:
        return path.is_file() and path.suffix in AudioFile.extensions
