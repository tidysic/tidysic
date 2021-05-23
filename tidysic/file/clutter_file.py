from tidysic.file.tagged_file import Taggable

class ClutterFile(Taggable):

    def __init__(self, path: Path):
        self.path = path