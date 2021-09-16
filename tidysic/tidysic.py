from pathlib import Path

from tidysic.organizer import Organizer
from tidysic.parser.tree import Tree
from tidysic.settings.parser import parse_settings
from tidysic.settings.structure import default_structure


class Tidysic:
    def __init__(self, source: str, target: str, settings_file: str) -> None:
        self._tree = Tree(Path(source))
        self._target = Path(target)

        structure = default_structure
        if settings_file:
            structure = parse_settings(settings_file)
        else:
            folder_settings_file = self._target / ".tidysic"
            if folder_settings_file.exists():
                structure = parse_settings(str(folder_settings_file))
        self._organizer = Organizer(structure)

    def run(self) -> None:
        self._organizer.organize(self._tree, self._target)
