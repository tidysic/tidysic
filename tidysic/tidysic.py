from pathlib import Path
from typing import Optional

from tidysic.organizer import CollisionException, Organizer
from tidysic.parser import Tree
from tidysic.settings.structure import Structure


class Tidysic:
    def __init__(self, source: str, target: str, settings_path: Optional[Path]) -> None:
        self._tree = Tree(Path(source))
        self._target = Path(target)

        if not settings_path:
            settings_path = self._target / ".tidysic"

        structure = Structure.build(settings_path)
        self._organizer = Organizer(structure)

    def run(self) -> None:
        try:
            self._organizer.organize(self._tree, self._target)
        except CollisionException as e:
            print(f"Error: {e}")
            print("They are the following:")
            for file in e.files:
                print(file.path)
            print(
                "Consider adapting the structure using different tags to differentiate them."
            )
