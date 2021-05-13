from pathlib import Path

from tidysic.parser.audio_file import AudioFile
from tidysic.parser.tree import Tree


def test_tree():
    tree = Tree(Path('tests/music'))

    def iter(root: Tree):
        assert isinstance(root, Tree)

        for audio_file in root.audio_files:
            assert isinstance(audio_file, AudioFile)

        for clutter_file in root.clutter_files:
            assert isinstance(clutter_file, Path)

        for child in root.children:
            iter(child)

    iter(tree)
