from enum import Enum
from tinytag import TinyTag


class Tag(Enum):

    Title = 1
    Artist = 2
    Album = 3
    Year = 4
    Track = 5
    Genre = 6

    def __str__(self):
        return self.name


def get_tags(file):
    '''
    Returns the tags of the given file as a dict
    '''
    tinytags = TinyTag.get(file)
    return {
        Tag.Title: tinytags.title,
        Tag.Artist: tinytags.artist,
        Tag.Album: tinytags.album,
        Tag.Year: tinytags.year,
        Tag.Track: tinytags.track,
        Tag.Genre: tinytags.genre
    }