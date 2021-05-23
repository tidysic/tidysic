from pathlib import Path

from itertools import chain
from functools import reduce
from typing import Optional

from tidysic.file.audio_file import AudioFile
from tidysic.file.tagged_file import TaggedFile
from tidysic.file.taggable import Taggable


class Tree:
    """
    Recursively parsed Tree, for easily accessing its file structure.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

        self.children: set['Tree'] = set()
        self.audio_files: set[AudioFile] = set()
        self.clutter_files: set[TaggedFile] = set()
        self.common_tags: Optional[Taggable] = None

        self._parse()

    def _parse(self) -> None:
        """
        Parse the `Tree`, grouping each file in one of the three categories,
        namely (i) a child folder, (ii) an audio file or (iii) a clutter file.
        Children folders are recursively parsed.
        """
        for path in self._root.iterdir():
            if path.is_dir():
                child = Tree(path)
                if child._contains_tags():
                    self.children.add(child)
                else:
                    self.clutter_files.add(TaggedFile(path))
            elif AudioFile.is_audio_file(path):
                self.audio_files.add(AudioFile(path))
            else:
                self.clutter_files.add(TaggedFile(path))

        if self._contains_tags():
            self._tag_clutter()

    def _contains_tags(self) -> bool:
        """
        Returns True if this node or any of its children has audio files.
        """
        return (
            self.common_tags is not None
            or
            len(self.audio_files) > 0
            or
            any(
                child._contains_tags()
                for child in self.children
            )
        )

    def _tag_clutter(self):
        """
        Tags non-audio files with the tags common to all audio files in the same
        directory and subdirectories.
        """
        common_tags = self._find_common_tags()
        self._apply_tags_to_clutter(common_tags)

    def _find_common_tags(self) -> Taggable:
        """
        Finds the common tags shared by the given tagged objects.
        """
        assert self._contains_tags()

        if self.common_tags is not None:
            return self.common_tags

        children_tags = [
            child._find_common_tags()
            for child in self.children
            if child._contains_tags()
        ]
        all_tags = chain(self.audio_files, children_tags)
        self.common_tags = reduce(Taggable.intersection, all_tags)

        return self.common_tags

    def _apply_tags_to_clutter(self, tags: Taggable):
        """
        Tags clutter in this node with the given tags.

        Affects its children if they do not contain audio files.
        """
        for clutter_file in self.clutter_files:
            clutter_file.copy_tags_from(tags)
