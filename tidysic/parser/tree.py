from pathlib import Path

from itertools import chain
from functools import reduce

from tidysic.file.audio_file import AudioFile
from tidysic.file.clutter_file import ClutterFile
from tidysic.file.taggable import Taggable


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

        self._tag_clutter()

    def _contains_tags(self) -> bool:
        """
        Returns True if this node or any of its children has audio files.
        """
        return (
            len(self.audio_files) > 0
            or
            any([
                child._contains_tags()
                for child in self.children
            ])
        )

    def _apply_tags_to_clutter(self, tags: Taggable):
        """
        Tags clutter in this node with the given tags.

        Affects its children if they do not contain audio files.
        """
        for clutter_file in self.clutter_files:
            clutter_file.copy_tags_from(tags)

        for child in self.children:
            if not child._contains_tags():
                child._apply_tags_to_clutter(tags)

    def _tag_clutter(self):
        """
        Tags non-audio files with the tags common to all audio files in the same
        directory and subdirectories.
        """
        if self._contains_tags():
            common_tags = self._find_common_tags()
            self._apply_tags_to_clutter(common_tags)

    def _find_common_tags(self) -> Taggable:
        """
        Finds the common tags shared by the given tagged objects.
        """
        children_tags = [
            child._find_common_tags()
            for child in self.children
            if child._contains_tags()
        ]
        all_tags = chain(self.audio_files, children_tags)
        return reduce(Taggable.intersection, all_tags)
