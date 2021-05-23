from collections import defaultdict
from pathlib import Path
from tidysic.file.clutter_file import ClutterFile

from tidysic.file.audio_file import AudioFile
from tidysic.file.taggable import Taggable
from functools import reduce

class Tree:
    """
    Recursively parsed Tree, for easily accessing its file structure.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

        self.children: set['Tree'] = set()
        self.audio_files: set[AudioFile] = set()
        self.clutter_files: set[ClutterFile] = set()

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
                self.clutter_files.add(ClutterFile(path))
        
        self._parse_clutter_files()

    
    def _parse_clutter_files(self):
        """
        Parse the `ClutterFile` of the `Tree` by assigning them tags shared by
        all the `AudioFile` of the `Tree`.
        """
        tags = self._find_tags_intersection()
        for clutter_file in self.clutter_files:
            clutter_file.copy_tags_from(tags)


    def _find_tags_intersection(self) -> Taggable:
        """
        Return a `Taggable` representing the interesection of all the
        `AudioFile` contianed in the `Tree`.
        """
        audio_files = self.all_audio_files()
        
        if len(audio_files) > 0:
            taggable_intersection = reduce(Taggable.intersection, audio_files)
            return taggable_intersection
        
        return Taggable()
    

    def all_audio_files(self) -> set[AudioFile]:
        """Return the set of all the `AudioFile` contained in the `Tree`."""
        audio_files = self.audio_files
        for child in self.children:
            audio_files.update(child.all_audio_files())
        return audio_files
