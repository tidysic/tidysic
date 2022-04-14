from itertools import chain
from pathlib import Path
from typing import Optional

from tidysic.file.audio_file import AudioFile
from tidysic.file.taggable import Taggable
from tidysic.file.tagged_file import TaggedFile
from tidysic.logger import Logger, Text

log = Logger()


class Tree:
    """
    Node of the tree that is built by parsing the input folder.

    Each node keeps track of its files (audio and otherwise), and the tags that are
    common to each of them.
    """

    def __init__(self, root: Path) -> None:
        self._root = root

        self.children: set["Tree"] = set()
        self.audio_files: set[AudioFile] = set()
        self.clutter_files: set[TaggedFile] = set()
        self.common_tags: Optional[Taggable] = None

        self._parse()

        log.info(
            [
                Text.assemble("Parsed directory ", (str(self._root), "path"), "."),
                f"Found {len(self.audio_files)} audio file(s).",
                f"Found {len(self.children)} subfolder(s) containing audio files.",
                f"Found {len(self.clutter_files)} clutter file(s).",
            ]
        )

    def _parse(self) -> None:
        """
        Parse the `Tree`, grouping each file in one of the three categories,
        namely (i) a child folder, (ii) an audio file or (iii) a clutter file.
        Children folders are recursively parsed.
        """
        for path in self._root.iterdir():
            if path.is_dir():
                child = Tree(path)
                if child.common_tags is not None:
                    self.children.add(child)
                else:
                    self.clutter_files.add(TaggedFile(path))
            elif AudioFile.is_audio_file(path):
                self.audio_files.add(AudioFile(path))
            else:
                self.clutter_files.add(TaggedFile(path))

        self._tag_clutter()

    def _tag_clutter(self) -> None:
        """
        Tags non-audio files with the tags common to all audio files in the same
        directory and subdirectories.
        """
        self._find_common_tags()
        self._apply_common_tags_to_clutter()

    def _find_common_tags(self) -> None:
        """
        Finds the common tags shared by the given tagged objects.
        """
        children_tags = [
            child.common_tags
            for child in self.children
            if child.common_tags is not None
        ]
        all_tags = tuple(chain(self.audio_files, children_tags))

        if len(all_tags) > 0:
            self.common_tags = Taggable.intersection(all_tags)

    def _apply_common_tags_to_clutter(self) -> None:
        """
        Tags clutter in this node with the given tags.

        Affects its children if they do not contain audio files.
        """
        if self.common_tags is not None:
            for clutter_file in self.clutter_files:
                clutter_file.copy_tags_from(self.common_tags)

    def clean_up(self) -> None:
        """
        Traverse its children and removes any empty directory.

        Running this will not result in the deletion of folders already empty before
        running the organizer, since these are considered clutter.
        """
        for child in self.children:
            child.clean_up()

        if not any(self._root.iterdir()):
            self._root.rmdir()
            log.info(
                Text.assemble(
                    "Deleted empty directory ", (self._root.name, "path"), "."
                )
            )
