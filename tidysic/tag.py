from enum import Enum


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

    @staticmethod
    def numeric_tags() -> set['Tag']:
        """
        Returns the set of all tags whose values are integer.
        """
        return {
            Tag.Track,
            Tag.Year
        }
