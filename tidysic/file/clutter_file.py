from pathlib import Path

from tidysic.file.taggable import Taggable


class ClutterFile(Taggable):

    def __init__(self, path: Path):
        self.path: Path = path

    def __hash__(self):
        return hash(self.path)
