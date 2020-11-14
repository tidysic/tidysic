from unittest import TestCase
import os

from tidysic.os_utils import project_test_folder, get_audio_files
from tidysic.tag import Tag
from tidysic.audio_file import AudioFile
from tidysic.algorithms import create_structure


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

        tree = create_structure(
            files,
            [Tag.Artist, Tag.Album],
            guess=False,
            dry_run=True
        )
        self.assertEqual(len(tree.unordered), 0)
        self.assertIsInstance(tree.ordered, dict)
        self.assertEqual(len(tree.ordered.keys()), 1)

        for artist_name, artist_subtree in tree.ordered.items():
            self.assertEqual(artist_name, 'L\'Artiste')
            self.assertEqual(len(artist_subtree.unordered), 0)
            self.assertIsInstance(artist_subtree.ordered, dict)
            self.assertEqual(len(artist_subtree.ordered.keys()), 1)

            for album_name, songs in artist_subtree.ordered.items():
                self.assertEqual(album_name, 'L\'Album')
                self.assertIsInstance(songs, list)
                self.assertEqual(len(songs), 1)

                song = songs[0]
                self.assertListEqual(files, [song])

        format = '{title}'
        self.assertEqual(song.build_file_name(format), 'Le Titre.mp3')

    def test_guess(self):

        path = os.path.join(
            AlgorithmTest.music_folder,
            'Missing Artist - No Title'
        )
        files = get_audio_files(path)

        # Needed in order to test without user input
        AudioFile.accept_all_guesses = True

        tree = create_structure(
            files,
            [Tag.Artist],
            guess=True,
            dry_run=False
        )

        self.assertEqual(len(tree.ordered), 1)
        for artist, songs in tree.ordered.items():
            song = songs[0]
            self.assertEqual(song.tags[Tag.Artist], 'Missing Artist')
            self.assertEqual(song.tags[Tag.Title], 'No Title')
