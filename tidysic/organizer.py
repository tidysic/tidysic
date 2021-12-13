import shutil
from dataclasses import dataclass
from pathlib import Path

from tidysic.file.audio_file import AudioFile
from tidysic.file.tagged_file import TaggedFile
from tidysic.parser.tree import Tree
from tidysic.settings.structure import Structure


@dataclass
class _Operation:

    file: TaggedFile
    target: Path

    def copy(self):
        self.target.parent.mkdir(parents=True, exist_ok=True)
        if self.file.path.is_dir():
            shutil.copytree(self.file.path, self.target)
        else:
            shutil.copyfile(self.file.path, self.target)

    def move(self):
        self.target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(self.file.path, self.target)


class Organizer:
    def __init__(self, structure: Structure) -> None:
        self._structure = structure

        self._operations: list[_Operation] = []

    def organize(self, tree: Tree, target: Path) -> None:
        self._operations = []
        self._build_operations(tree, target)

        for operation in self._operations:
            operation.copy()

    def _build_operations(self, tree: Tree, target: Path) -> None:
        for file in tree.audio_files | tree.clutter_files:
            path = target / self._build_target_path(file)
            self._operations.append(_Operation(file=file, target=path))

        for child in tree.children:
            self._build_operations(child, target)

    def _build_target_path(self, tagged_file: TaggedFile) -> Path:
        path = Path()
        for step in self._structure.folders:
            folder_name = step.formatted_string.write(tagged_file)
            path /= folder_name
        if isinstance(tagged_file, AudioFile):
            filename = (
                self._structure.track_format.write(tagged_file) + tagged_file.extension
            )
        else:
            filename = tagged_file.path.name
        path /= filename
        return path
