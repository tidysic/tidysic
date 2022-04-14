from pathlib import Path

from tidysic.file.taggable import Taggable


class TaggedFile(Taggable):
    """
    Base class for any file that can hold tags. Audio files are such files
    obviously, but so are folders containing audio files.
    """
    def __init__(self, path: Path):
        self.path: Path = path

    def __hash__(self) -> int:
        return hash(self.path)
