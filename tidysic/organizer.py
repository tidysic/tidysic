import shutil
from pathlib import Path
from tidysic.file.taggable import Taggable

from tidysic.file.audio_file import AudioFile
from tidysic.file.clutter_file import ClutterFile
from tidysic.parser.tree import Tree


class Organizer:

    def __init__(self, pattern: str) -> None:
        self._attributes = pattern.split('/')

    def organize(self, tree: Tree, target: Path) -> None:
        for audio_file in tree.audio_files:
            path = target / self._build_path(audio_file)
            path.mkdir(parents=True, exist_ok=True)
            Organizer._copy_audio_file(parent=path, audio_file=audio_file)
        
        for clutter_file in tree.clutter_files:
            path = target / self._build_path(clutter_file)
            path.mkdir(parents=True, exist_ok=True)
            Organizer._copy_clutter_file(parent=path, clutter_file=clutter_file)

        for child in tree.children:
            self.organize(child, target)

    def _build_path(self, taggable: Taggable) -> Path:
        path = Path()
        for attribute in self._attributes:
            print(attribute)
            path = path / getattr(taggable, attribute)
        return path

    @staticmethod
    def _copy_audio_file(parent: Path, audio_file: AudioFile) -> None:
        audio_path = parent / audio_file.get_title_with_extension()
        shutil.copyfile(audio_file.path, audio_path)
    
    @staticmethod
    def _copy_clutter_file(parent: Path, clutter_file: ClutterFile) -> None:
        clutter_path = parent / clutter_file.path.stem
        shutil.copyfile(clutter_file.path, clutter_path)
