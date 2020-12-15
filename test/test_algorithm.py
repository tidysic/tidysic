from unittest import TestCase
import os
from shutil import copytree, rmtree

from tidysic.os_utils import project_test_folder
from tidysic.tag import Tag
from tidysic.audio_file import AudioFile
from tidysic.algorithms import (
    scan_folder,
    create_structure,
    move_files,
    organize,
    TreeNode,
)


class AlgorithmTest(TestCase):

    original_music_root = os.path.join(
        project_test_folder(),
        'music'
    )

    test_root = os.path.join(
        project_test_folder(),
        'music_copy'
    )

    def setUp(self):
        copytree(
            AlgorithmTest.original_music_root,
            AlgorithmTest.test_root
        )
    
    def tearDown(self):
        rmtree(
            AlgorithmTest.test_root
        )

    def test_normal(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'normal'
        )
        files, _ = scan_folder(path, False, False)
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
        format = '{{title}}'
        self.assertEqual(song.fill_formatted_str(format), 'Le Titre')
        self.assertEqual(song.build_file_name(format), 'Le Titre.mp3')

    def test_guess(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'Missing Artist - No Title'
        )
        # Needed in order to test without user input
        AudioFile.accept_all_guesses = True

        files, _ = scan_folder(path, True, False)

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
            AlgorithmTest.test_root,
            'a bunch of illegal characters'
        )
        files, _ = scan_folder(path, False, False)

        root_nodes = create_structure(
            files,
            [Tag.Artist],
            guess=True,
            dry_run=True
        )

        song = root_nodes[0].children[0]
        formats = [
            '{{artist}}',
            '{{artist}} - {{title}}'
        ]
        file_name = song.build_file_name(formats[-1])
        self.assertIn('/', file_name)

        move_files(
            root_nodes,
            path,
            formats,
            with_clutter=False,
            dry_run=False,
            verbose=False
        )

    def test_format(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'format title-artist-album'
        )
        files, _ = scan_folder(path, False, False)

        root_nodes = create_structure(
            files,
            [Tag.Artist],
            guess=True,
            dry_run=True
        )

        song = root_nodes[0].children[0]
        format = '{{title}} {{artist}} {{album} !}{ {genre}}'
        file_name = song.fill_formatted_str(format)

        self.assertEqual(file_name, 'You did it !')

    def test_missing_order_tag(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'missing album tag'
        )
        files, _ = scan_folder(path, False, False)

        root_nodes = create_structure(
            files,
            [Tag.Album],
            guess=True,
            dry_run=True
        )

        album_node: TreeNode = root_nodes[0]
        self.assertEqual(album_node.name, 'Unknown Album')

    def test_clutter(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'clutter test'
        )

        organize(
            path,
            path,
            with_album=True,
            with_clutter=True,
            guess=False,
            dry_run=False,
            verbose=True
        )

        artist_folder = os.path.join(path, 'Artist Name')
        self.assertTrue(os.path.isdir(artist_folder))

        artist_clutter = os.path.join(artist_folder, 'artist_clutter')
        self.assertTrue(os.path.isfile(artist_clutter))

        album_folder = os.path.join(artist_folder, 'Album Name')
        self.assertTrue(os.path.isdir(album_folder))

        album_clutter_dir = os.path.join(album_folder, 'album_clutter')
        print(album_clutter_dir)
        self.assertTrue(os.path.isdir(album_clutter_dir))

        album_clutter1 = os.path.join(album_clutter_dir, 'clutter1')
        album_clutter2 = os.path.join(album_clutter_dir, 'clutter2')
        self.assertTrue(os.path.isfile(album_clutter1))
        self.assertTrue(os.path.isfile(album_clutter2))
