
from pathlib import Path

from tidysic.organizer import Organizer
from tidysic.parser.tree import Tree


class Tidysic:

    def __init__(self, source: str, target: str, pattern: str) -> None:
        self._tree = Tree(Path(source))
        self._target = Path(target)
        self._organizer = Organizer(pattern)

    def run(self) -> None:
        self._organizer.organize(self._tree, self._target)
