from enum import Enum
from mutagen import File as MutagenFile


class Tag(Enum):
    '''
    Tags supported by Tidysic.

    The name is a human-readable description of the tag, whereas the value is
    an the actual ID3 tag name
    '''

    Title = 'title'
    Artist = 'artist'
    Album = 'album'
    Year = 'date'
    Track = 'tracknumber'
    Genre = 'genre'

    def __str__(self):
        return self.name


def get_tags(file):
    '''
    Returns the tags of the given file as a dict
    '''
    tags = MutagenFile(file).tags
    return {
        tag: tags[tag.value][0] if tag.value in tags else None
        for tag in Tag
    }
