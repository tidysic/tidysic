
from pathlib import Path

from tidysic.parser.tree import Tree
from tidysic.organizer import Organizer

class Tidysic:

    def __init__(self, source_path: str, dest_path: str) -> None:
        self._dest_path = Path(dest_path)
        self._tree = Tree(Path(source_path))
        self._organizer = Organizer(['artist', 'album']) # sort by artist->album->title
        # self._organizer = Organizer(['genre'])  # sort by genre->title

    def run(self):
        self._organizer.organize(self._tree, self._dest_path)
