from pathlib import Path

from tidysic.organizer import Organizer
from tidysic.parser import Tree
from tidysic.settings.structure import Structure


class Tidysic:
    def __init__(self, source: str, target: str, settings_path: str) -> None:
        self._tree = Tree(Path(source))
        self._target = Path(target)

        structure = Structure.get_default()
        if settings_path:
            with open(settings_path, "r") as settings:
                structure = Structure.parse(settings.read())
        else:
            folder_settings_file = self._target / ".tidysic"
            if folder_settings_file.exists():
                structure = Structure.parse(folder_settings_file.read_text())
        self._organizer = Organizer(structure)

    def run(self) -> None:
        self._organizer.organize(self._tree, self._target)
