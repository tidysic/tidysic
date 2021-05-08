import shutil
from pathlib import Path

from tidysic.parser.audio_file import AudioFile
from tidysic.parser.tree import Tree


class Tidysic:

    def __init__(self, source_path: str, dest_path: str) -> None:
        self._dest_path = Path(dest_path)
        self._tree = Tree(Path(source_path))

    def run(self):
        artists = self._tree.sort()

        for artist in artists.keys():
            for album in artists[artist].keys():
                album_path = self._create_album_folder(artist, album)
                for music in artists[artist][album]:
                    self._copy_music(music, album_path)

    def _create_album_folder(self, artist: str, album: str):
        album_path = self._dest_path / artist / album
        album_path.mkdir(parents=True)
        return album_path

    def _copy_music(self, music: AudioFile, album_path: Path) -> None:
        shutil.copy(
            music.path,
            album_path / music.get_title_with_extension()
        )
