from pathlib import Path

from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError
from tidysic.file.tagged_file import TaggedFile


class AudioFile(TaggedFile):
    """
    Audio file with its tags parsed by mutagen, for easy acces.
    """

    extensions = {
        ".flac",
        ".mp3",
        ".ogg",
        ".wav",
    }

    def __init__(self, path: Path):
        super().__init__(path)
        self.extension: str = self.path.suffix

        self._parse()

    def _parse(self) -> None:
        tags = self._get_mutagen_tags()
        self.set_tags(tags)

    def _get_mutagen_tags(self) -> dict[str, str]:
        try:
            return {k: v[0] for k, v in EasyID3(self.path.resolve()).items()}
        except ID3NoHeaderError:
            return dict()

    @staticmethod
    def is_audio_file(path: Path) -> bool:
        """Return true if the given file is a (supported) audio file.

        Args:
            path (Path): Path of the file to test.

        Returns:
            bool: True if the given file is an audio file.
        """
        return path.is_file() and path.suffix in AudioFile.extensions
