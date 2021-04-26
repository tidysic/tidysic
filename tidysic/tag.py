from enum import Enum
from typing import Union


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
        '''
        Returns the set of all tags whose values are integer.
        '''
        return {
            Tag.Track,
            Tag.Year
        }

    @staticmethod
    def validate_input(tag: 'Tag', value: str) -> Union[str, int]:
        '''
        Returns the value provided for the given tag with the correct type.

        Raises a ValueError if the given value isn't valid.
        '''
        if tag in {Tag.Track, Tag.Year}:
            # Value is expected to be an int
            try:
                return int(value)

            except ValueError:
                raise ValueError(
                    f'{tag.name} expects an integer, '
                    f'{value} was provided.'
                )
        
        else:
            # Value is expected to be a string
            return value
