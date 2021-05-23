from pathlib import Path

from tidysic.file.audio_file import AudioFile

path = Path('tests/music/normal/normal.mp3')
audio_file = AudioFile(path)


def test_audio_file_extension():
    assert audio_file.extension in AudioFile.extensions


def test_is_audio_file():
    assert AudioFile.is_audio_file(path)
    assert not AudioFile.is_audio_file(Path('tests/music/normal'))
