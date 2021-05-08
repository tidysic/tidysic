from tidysic.directory import Directory

def test_directory():
    directory = Directory('./tests/music')
    len(directory.children) == 6
    len(directory.audio_files) == 0
    len(directory.clutter_files) == 0