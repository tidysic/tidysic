from unittest import TestCase
import os

from tidysic.os_utils import project_test_folder, get_audio_files
from tidysic.tag import Tag
from tidysic.audio_file import AudioFile
from tidysic.algorithms import create_structure, move_files, TreeNode


class AlgorithmTest(TestCase):

    music_folder = os.path.join(
        project_test_folder(),
        'music'
    )

    def test_normal(self):
        path = os.path.join(
            AlgorithmTest.music_folder,
            'normal'
        )
        files = get_audio_files(path)
        self.assertEqual(len(files), 1)

        root_nodes = create_structure(
            files,
            [Tag.Artist, Tag.Album],
            guess=False,
            dry_run=True
        )
        self.assertEqual(len(root_nodes), 1)

        artist_node: TreeNode = root_nodes[0]
        self.assertIsInstance(artist_node, TreeNode)
        self.assertEqual(artist_node.tag, Tag.Artist)
        self.assertEqual(artist_node.name, 'L\'Artiste')
        self.assertEqual(len(artist_node.children), 1)

        album_node: TreeNode = artist_node.children[0]
        self.assertIsInstance(album_node, TreeNode)
        self.assertEqual(album_node.tag, Tag.Album)
        self.assertEqual(album_node.name, 'L\'Album')
        self.assertEqual(len(album_node.children), 1)
        self.assertListEqual(album_node.children, files)

        song: AudioFile = album_node.children[0]
        self.assertIsInstance(song, AudioFile)
        format = '{title}'
        self.assertEqual(song.build_name(format), 'Le Titre')
        self.assertEqual(song.build_file_name(format), 'Le Titre.mp3')

    def test_guess(self):
        path = os.path.join(
            AlgorithmTest.music_folder,
            'Missing Artist - No Title'
        )
        files = get_audio_files(path)

        # Needed in order to test without user input
        AudioFile.accept_all_guesses = True

        root_nodes = create_structure(
            files,
            [Tag.Artist],
            guess=True,
            dry_run=False  # Need to actually change the file
        )

        self.assertEqual(len(root_nodes), 1)
        song = root_nodes[0].children[0]
        self.assertEqual(song.tags[Tag.Artist], 'Missing Artist')
        self.assertEqual(song.tags[Tag.Title], 'No Title')

    def test_illegal_characters(self):
        path = os.path.join(
            AlgorithmTest.music_folder,
            'a bunch of illegal characters'
        )
        files = get_audio_files(path)

        root_nodes = create_structure(
            files,
            [Tag.Artist],
            guess=True,
            dry_run=True
        )

        song = root_nodes[0].children[0]
        file_name = song.build_file_name('{artist} - {title}')
        self.assertIn('/', file_name)

        move_files(
            root_nodes,
            path,
            '{artist} - {title}',
            dry_run=False
        )

    def test_format(self):
        path = os.path.join(
            AlgorithmTest.music_folder,
            'format title-artist-album'
        )
        files = get_audio_files(path)

        root_nodes = create_structure(
            files,
            [Tag.Artist],
            guess=True,
            dry_run=True
        )

        song = root_nodes[0].children[0]
        format = '{title} {artist} {album}'
        file_name = song.build_name(format)

        self.assertEqual(file_name, 'You did it')

    def test_missing_order_tag(self):
        path = os.path.join(
            AlgorithmTest.music_folder,
            'missing album tag'
        )
        files = get_audio_files(path)

        root_nodes = create_structure(
            files,
            [Tag.Album],
            guess=True,
            dry_run=True
        )

        album_node: TreeNode = root_nodes[0]
        self.assertEqual(album_node.name, 'Unknown Album')
