from pathlib import Path

from tidysic.organizer import CollisionException, Organizer
from tidysic.parser.tree import Tree
from tidysic.settings.parser import parse_settings
from tidysic.settings.structure import default_structure


class Tidysic:
    def __init__(self, source: str, target: str, settings_path: str) -> None:
        self._tree = Tree(Path(source))
        self._target = Path(target)

        structure = default_structure
        if settings_path:
            with open(settings_path, "r") as settings:
                structure = parse_settings(settings.read())
        else:
            folder_settings_file = self._target / ".tidysic"
            if folder_settings_file.exists():
                structure = parse_settings(folder_settings_file.read_text())
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
