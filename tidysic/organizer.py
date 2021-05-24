import shutil
from pathlib import Path

from tidysic.file.audio_file import AudioFile
from tidysic.file.tagged_file import TaggedFile
from tidysic.parser.tree import Tree


class Organizer:
    def __init__(self, pattern: str) -> None:
        self._attributes = pattern.split("/")

    def organize(self, tree: Tree, target: Path) -> None:
        for audio_file in tree.audio_files:
            path = target / self._build_path(audio_file)
            path.mkdir(parents=True, exist_ok=True)
            Organizer._copy_file(parent=path, audio_file=audio_file)

        for clutter_file in tree.clutter_files:
            path = target / self._build_path(clutter_file)
            path.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(clutter_file.path, path)

        for child in tree.children:
            self.organize(child, target)

    def _build_path(self, tagged_file: TaggedFile) -> Path:
        path = Path()
        for attribute in self._attributes:
            folder_name = getattr(tagged_file, attribute)
            if folder_name is None:
                folder_name = f"Unknown {attribute}"
            path = path / folder_name
        return path

    @staticmethod
    def _copy_file(parent: Path, audio_file: AudioFile) -> None:
        audio_path = parent / audio_file.get_title_with_extension()
        shutil.copyfile(audio_file.path, audio_path)
