import shutil
from pathlib import Path

from tidysic.parser.audio_file import AudioFile
from tidysic.parser.tree import Tree


class Organizer:

    def __init__(self, attributes: list[str]) -> None:
        self._attributes = attributes

    def organize(self, tree: Tree, dest_path: Path):
        for audio_file in tree.audio_files:
            path = dest_path / self._build_path(audio_file)
            path.mkdir(parents=True, exist_ok=True)
            Organizer._copy_file(parent=path, audio_file=audio_file)

        for child in tree.children:
            self.organize(child, dest_path)

    def _build_path(self, audio_file: AudioFile) -> Path:
        path = Path()
        for attribute in self._attributes:
            path = path / getattr(audio_file, attribute)
        return path

    @staticmethod
    def _copy_file(parent: Path, audio_file: AudioFile):
        audio_path = parent / audio_file.get_title_with_extension()
        shutil.copyfile(audio_file.path, audio_path)
