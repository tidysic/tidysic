from collections import defaultdict
from pathlib import Path

from tidysic.parser.audio_file import AudioFile


class Tree:
    """
    Recursively parsed Tree, for easily accessing its file structure.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

        self.children: set['Tree'] = set()
        self.audio_files: set[AudioFile] = set()
        self.clutter_files: set[Path] = set()

        self._parse()

    def _parse(self) -> None:
        """
        Parse the `Tree`, grouping each file in one of the three categories,
        namely (i) a child folder, (ii) an audio file or (iii) a clutter file.
        Children folders are recursively parsed.
        """
        for path in self._root.iterdir():
            if path.is_dir():
                self.children.add(Tree(path))
            elif AudioFile.is_audio_file(path):
                self.audio_files.add(AudioFile(path))
            else:
                self.clutter_files.add(path)
