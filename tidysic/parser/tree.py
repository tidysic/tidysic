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
        self.clutter_files: set[str] = set()

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
                self.clutter_files.add(path.name)

    def sort(self, sorted_tree=defaultdict(lambda: defaultdict(set))):
        """
        Sort the tree by generating a structure: 

            Artist->Album->Title
        
        Return this structure as a dictionary, i.e., you can access the
        structure with:

            sorted_tree[artist][album] = set(titles)
        """
        for audio_file in self.audio_files:
            sorted_tree[audio_file.artist][audio_file.album].add(audio_file)
        
        for child in self.children:
            child.sort(sorted_tree=sorted_tree)

        return sorted_tree