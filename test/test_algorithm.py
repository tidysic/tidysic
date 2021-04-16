from unittest import TestCase
import os
from shutil import copytree, rmtree

from tidysic.os_utils import project_test_folder
from tidysic.tag import Tag
from tidysic.audio_file import AudioFile
from tidysic.tidysic import TreeNode
from tidysic.formatted_string import FormattedString
from tidysic.ordering import OrderingStep, Ordering

from tidysic import Tidysic


class AlgorithmTest(TestCase):

    original_music_root = os.path.join(
        project_test_folder(),
        'music'
    )

    test_root = os.path.join(
        project_test_folder(),
        'music_copy'
    )

    @classmethod
    def setUpClass(cls):
        copytree(
            AlgorithmTest.original_music_root,
            AlgorithmTest.test_root
        )

    @classmethod
    def tearDownClass(cls):
        rmtree(
            AlgorithmTest.test_root
        )

    def test_normal(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'normal'
        )
        tidysic = Tidysic(input_dir=path, output_dir=path)
        tidysic.scan_folder()
        self.assertEqual(len(tidysic.audio_files), 1)

        tidysic.create_structure()
        self.assertEqual(len(tidysic.root_nodes), 1)

        artist_node: TreeNode = tidysic.root_nodes[0]
        self.assertIsInstance(artist_node, TreeNode)
        self.assertEqual(artist_node.tag, Tag.Artist)
        self.assertEqual(artist_node.name, 'L\'Artiste')
        self.assertEqual(len(artist_node.children), 1)

        album_node: TreeNode = artist_node.children[0]
        self.assertIsInstance(album_node, TreeNode)
        self.assertEqual(album_node.tag, Tag.Album)
        self.assertEqual(album_node.name, 'L\'Album')
        self.assertEqual(len(album_node.children), 1)
        self.assertListEqual(album_node.children, tidysic.audio_files)

        song: AudioFile = album_node.children[0]
        self.assertIsInstance(song, AudioFile)
        formatted_string = FormattedString('{{title}}')
        self.assertEqual(formatted_string.build(song.tags), 'Le Titre')
        self.assertEqual(
            song.build_file_name(formatted_string),
            'Le Titre.mp3'
        )

    def test_guess(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'Missing Artist - No Title'
        )
        # Needed in order to test without user input
        AudioFile.accept_all_guesses = True

        tidysic = Tidysic(input_dir=path, output_dir=path, guess=True)
        tidysic.ordering = Ordering([
            OrderingStep(Tag.Artist, FormattedString("{{artist}}")),
            OrderingStep(Tag.Title, FormattedString("{{title}}"))
        ])

        tidysic.scan_folder()
        tidysic.create_structure()

        self.assertEqual(len(tidysic.root_nodes), 1)
        song = tidysic.root_nodes[0].children[0]
        self.assertEqual(song.tags[Tag.Artist], 'Missing Artist')
        self.assertEqual(song.tags[Tag.Title], 'No Title')

    def test_illegal_characters(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'a bunch of illegal characters'
        )

        tidysic = Tidysic(input_dir=path, output_dir=path, guess=True)
        tidysic.ordering = Ordering([
            OrderingStep(Tag.Artist, FormattedString('{{artist}}')),
            OrderingStep(Tag.Title, FormattedString('{{artist}} - {{title}}'))
        ])
        tidysic.scan_folder()
        tidysic.create_structure()

        song = tidysic.root_nodes[0].children[0]
        formatted_string = tidysic.ordering.steps[1].format
        file_name = song.build_file_name(formatted_string)
        self.assertIn('/', file_name)

        tidysic.move_files()

    def test_format(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'format title-artist-album'
        )
        tidysic = Tidysic(input_dir=path, output_dir=path)
        tidysic.ordering = Ordering([
            OrderingStep(Tag.Artist, FormattedString("{{artist}}"))
        ])
        tidysic.scan_folder()
        song = tidysic.audio_files[0]

        formatted_string = FormattedString(
            '{{title}} {{artist}} {{album} !}{ {genre}}'
        )
        song_name = formatted_string.build(song.tags)
        self.assertEqual(song_name, 'You did it !')

    def test_missing_order_tag(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'missing album tag'
        )
        tidysic = Tidysic(input_dir=path, output_dir=path)
        tidysic.ordering = Ordering([
            OrderingStep(Tag.Album, FormattedString("{{album}}")),
            OrderingStep(Tag.Title, FormattedString("{{title}}"))
        ])
        tidysic.scan_folder()
        tidysic.create_structure()

        album_node: TreeNode = tidysic.root_nodes[0]
        self.assertEqual(album_node.name, 'Unknown Album')

    def test_clutter(self):
        path = os.path.join(
            AlgorithmTest.test_root,
            'clutter test'
        )
        tidysic = Tidysic(
            input_dir=path,
            output_dir=path,
            with_clutter=True
        )
        tidysic.organize()

        artist_folder = os.path.join(path, 'Artist Name')
        self.assertTrue(os.path.isdir(artist_folder))

        artist_clutter = os.path.join(artist_folder, 'artist_clutter')
        self.assertTrue(os.path.isfile(artist_clutter))

        album_folder = os.path.join(artist_folder, 'Album Name')
        self.assertTrue(os.path.isdir(album_folder))

        album_clutter_dir = os.path.join(album_folder, 'album_clutter')
        self.assertTrue(os.path.isdir(album_clutter_dir))

        album_clutter1 = os.path.join(album_clutter_dir, 'clutter1')
        album_clutter2 = os.path.join(album_clutter_dir, 'clutter2')
        self.assertTrue(os.path.isfile(album_clutter1))
        self.assertTrue(os.path.isfile(album_clutter2))
