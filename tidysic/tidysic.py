from pathlib import Path
from typing import Optional

from tidysic.organizer import Organizer
from tidysic.parser import Tree
from tidysic.settings.structure import Structure


class Tidysic:
    def __init__(
        self, source: Path, target: Path, settings_path: Optional[Path]
    ) -> None:
        self._tree = Tree(source)
        self._target = target

        if not settings_path:
            settings_path = self._target / ".tidysic"

        structure = Structure.build(settings_path)
        self._organizer = Organizer(structure)

    def run(self) -> None:
        self._organizer.organize(self._tree, self._target)
