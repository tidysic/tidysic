from .tag import Tag, get_tags


class AudioFile(object):

    def __init__(self, file):

        self.file = file
        self.tags = get_tags(file)
        self.guessed_tags = None

    def guess_tags(self):
        pass

    def build_file_name(self, format: str):
        from .os_utils import file_extension  # Avoid circular import
        return format.format(
            title=self.tags[Tag.Title],
            album=self.tags[Tag.Album],
            artist=self.tags[Tag.Artist],
            year=self.tags[Tag.Year],
            track=int(self.tags[Tag.Track]),
            genre=self.tags[Tag.Genre]
        ) + file_extension(self.file)
