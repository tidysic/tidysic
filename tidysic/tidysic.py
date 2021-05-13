
from pathlib import Path

from tidysic.parser.tree import Tree
from tidysic.organizer import Organizer

class Tidysic:

    def __init__(self, source: str, target: str, pattern: list[str]) -> None:
        self._tree = Tree(Path(source))
        self._target = Path(target)
        self._organizer = Organizer(pattern)

    def run(self) -> None:
        self._organizer.organize(self._tree, self._target)
