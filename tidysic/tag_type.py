from enum import Enum


class Tag(Enum):

    Title = 1
    Artist = 2
    Album = 3
    Year = 4
    Track = 5
    Genre = 6

    def __str__(self):
        return self.name
