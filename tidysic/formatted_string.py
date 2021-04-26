from typing import Any
import re

from tidysic.tag import Tag


class FormattedString:
    '''
    A formatted string contains tag keys written in double
    curly brackets, such as `{{artist}}`.

    The double brackets are useful if you want to insert text
    that will only be displayed if the tag is not None. For
    instance, the string

    `{{track}. }{{title}}`

    will become

    `1. Intro`

    if the `track` tag is defined. Otherwise, it will just
    be

    `Intro`

    The `year` and `track` tags can be formatted as usual, seeing
    as they are integer values. This way, track numbers may be
    padded using:

    `{{track:02d}. }{{title}}`
    '''

    def __init__(self, string: str):
        try:
            FormattedString.assert_well_written(string)
        except AssertionError as e:
            raise ValueError(
                f'Could not create FormattedString from {string}: {e}'
            )

        self._str = string

    def build(self, tags: dict[Tag, Any]) -> str:
        pattern = r'\{(.*?\{(\w+)(:.+?)?\}.*?)\}'
        matches = re.findall(pattern, self._str)

        return_string = self._str

        substitutions = []
        for to_substitute, tag_name, format_spec in matches:

            value = None
            tag = Tag[tag_name.capitalize()]

            value = tags[tag]
            if tag in {Tag.Year, Tag.Track} and value:
                value = int(value)
            if tag in {Tag.Title, Tag.Artist, Tag.Album} and not value:
                value = f'Unknown {tag.name}'

            formattable = to_substitute.replace(
                f'{{{tag_name}{format_spec}}}',
                f'{{{format_spec}}}'
            )
            substitutions.append((
                f'{{{to_substitute}}}',
                formattable.format(value) if value else ''
            ))

        for old, new in substitutions:
            return_string = return_string.replace(old, new)

        return return_string

    @staticmethod
    def assert_well_written(string: str):
        '''
        Runs a series of assert statements that will pass only if the provided
        string has a correct format. Refer to the class' documentation for more
        info on the format.

        Args:
            string (str): String whose format to test.
        '''
        bracket_depth = 0
        current_tag_name = ''

        for i, char in enumerate(string):
            if char == '{':
                bracket_depth += 1
                assert bracket_depth <= 2, (
                    f'Too many opening brackets (col {i})'
                )

            elif char == '}':
                bracket_depth -= 1
                assert bracket_depth >= 0, (
                    f'Too many closing brackets (col {i})'
                )

                if bracket_depth == 0:
                    assert current_tag_name in {
                        tag.name.lower()
                        for tag in Tag
                    }, (
                        f'Invalid tag name {current_tag_name}'
                    )
                    current_tag_name = ''
            
            elif bracket_depth == 2:
                current_tag_name += char
