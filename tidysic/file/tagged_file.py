from pathlib import Path

from tidysic.file.taggable import Taggable


class TaggedFile(Taggable):
    def __init__(self, path: Path):
        self.path: Path = path

    def __hash__(self) -> int:
        return hash(self.path)
