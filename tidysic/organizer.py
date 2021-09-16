import shutil
from pathlib import Path

from tidysic.file.audio_file import AudioFile
from tidysic.file.tagged_file import TaggedFile
from tidysic.parser.tree import Tree
from tidysic.settings.formatted_string import FormattedString
from tidysic.settings.structure import Structure


class Organizer:
    def __init__(self, structure: Structure) -> None:
        self._structure = structure

    def organize(self, tree: Tree, target: Path) -> None:
        for audio_file in tree.audio_files:
            path = target / self._build_path(audio_file)
            path.mkdir(parents=True, exist_ok=True)
            Organizer._copy_file(
                parent=path,
                audio_file=audio_file,
                track_format=self._structure.track_format,
            )

        for clutter_file in tree.clutter_files:
            path = target / self._build_path(clutter_file)
            path.mkdir(parents=True, exist_ok=True)

            path /= clutter_file.path.name
            shutil.copyfile(clutter_file.path, path)

        for child in tree.children:
            self.organize(child, target)

    def _build_path(self, tagged_file: TaggedFile) -> Path:
        path = Path()
        for step in self._structure.folders:
            folder_name = step.formatted_string.write(tagged_file)
            path = path / folder_name
        return path

    @staticmethod
    def _copy_file(
        parent: Path, audio_file: AudioFile, track_format: FormattedString
    ) -> None:
        target_name = track_format.write(audio_file) + audio_file.extension
        audio_path = parent / target_name
        shutil.copyfile(audio_file.path, audio_path)
