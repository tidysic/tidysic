from pathlib import Path

from tidysic.file.audio_file import AudioFile
from tidysic.file.clutter_file import ClutterFile
from tidysic.parser.tree import Tree


def test_tree():
    tree = Tree(Path('tests/music'))

    def iter(root: Tree):
        assert isinstance(root, Tree)

        for audio_file in root.audio_files:
            assert isinstance(audio_file, AudioFile)

        for clutter_file in root.clutter_files:
            assert isinstance(clutter_file, ClutterFile)

        for child in root.children:
            iter(child)

    iter(tree)


def test_clutter():
    tree = Tree(Path('tests/music/clutter test'))

    assert len(tree.clutter_files) == 1
    artist_clutter = tree.clutter_files.pop()

    assert artist_clutter.artist == "Artist Name"
    assert artist_clutter.album is None

    assert len(tree.children) == 1
    album_node = tree.children.pop()
    assert len(album_node.clutter_files) == 0

    assert len(album_node.children) == 1
    album_clutter_node = album_node.children.pop()
    assert len(album_clutter_node.clutter_files) == 2

    for album_clutter in album_clutter_node.clutter_files:
        assert album_clutter.artist == "Artist Name"
        assert album_clutter.album == "Album Name"
        assert album_clutter.title is None
