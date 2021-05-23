from pathlib import Path

from typing import Iterator, Callable

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
        self._parse_non_audio()

    def _parse(self) -> None:
        """
        Parse the `Tree`, grouping each file in one of the three categories,
        namely (i) a child folder, (ii) an audio file or (iii) a clutter file.
        Children folders are recursively parsed.
        """
        for path in self._root.iterdir():
            if path.is_dir():
                child = Tree(path)
                if child.audio_files:
                    self.children.add(child)
                else:
                    self.clutter_files.add(ClutterFile(path))
            elif AudioFile.is_audio_file(path):
                self.audio_files.add(AudioFile(path))
            else:
                self.clutter_files.add(ClutterFile(path))

    def _parse_non_audio(self) -> None:
        """
        Tags non-audio files with the tags common to all audio files in the same
        directory and subdirectories.
        """
        _ = self._tag_clutter_and_return_common_tags()

    def _tag_clutter_and_return_common_tags(self) -> Taggable:
        """
        Tags non-audio files with the tags common to all audio files in the same
        directory and subdirectories, and returns the set of tags.
        """

        def all_tagged() -> Iterator[Taggable]:
            for audio_file in self.audio_files:
                yield audio_file
            
            for child in self.children:
                yield child._tag_clutter_and_return_common_tags()

        for t in all_tagged():
            print(t)

        common_tags = self._find_common_tags(all_tagged)
        print(common_tags)
        print()
        for clutter_file in self.clutter_files:
            clutter_file.copy_tags_from(common_tags)
        
        return common_tags

    @staticmethod
    def _find_common_tags(
        taggables: Callable[[], Iterator[Taggable]]
    ) -> Taggable:
        """
        Finds the common tags shared by the given tagged objects.
        """
        common_tags = Taggable()

        for tag_name in common_tags.get_tag_names():
            tag_values = set([
                getattr(tagged, tag_name)
                for tagged in taggables()
            ])
            if len(tag_values) == 1:
                tag_value = tag_values.pop()
                setattr(common_tags, tag_name, tag_value)

        return common_tags

