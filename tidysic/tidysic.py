from pathlib import Path
from typing import Optional

from tidysic.exceptions import log_and_exit_on_exception
from tidysic.organizer import Organizer
from tidysic.parser import Tree
from tidysic.settings.structure import Structure


@log_and_exit_on_exception
class Tidysic:
    """
    Wrapper for the whole process of tidying.

    Contains a parser and an organizer.
    """
    def __init__(
        self,
        source: Path,
        target: Path,
        move: bool,
        dry_run: bool,
        settings_path: Optional[Path]
    ) -> None:
        self._tree = Tree(source)
        self._target = target

        if not settings_path:
            settings_path = self._target / ".tidysic"

        structure = Structure.build(settings_path)
        self._organizer = Organizer(structure, move, dry_run)

    def run(self) -> None:
        """
        Runs the tidying.
        """
        self._organizer.organize(self._tree, self._target)
        self._tree.clean_up()
