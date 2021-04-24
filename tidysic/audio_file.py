from typing import Union, Optional

from mutagen import File as MutagenFile
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError

from tidysic.tag import Tag
from tidysic.formatted_string import FormattedString
from tidysic import logger


class ClutterFile(object):
    '''
    Class describing a non-audio file, that also contains all the tags that
    other audio files in the same folder share.
    '''

    def __init__(self, file):
        self.file = file
        self.tags = {}
        for tag in Tag:
            self.tags[tag] = None
        # Avoid circular imports
        from .os_utils import filename
        self.name = filename(file)


class AudioFile(object):
    '''
    Class describing a music file, and its associated tags
    '''

    def __init__(self, file):
        self.file = file
        self.set_tags_from_file()

    def ask_and_set_tag(self, tag: Tag) -> Union[str, int]:
        '''
        Ask the user to provide one of the file's tags, and set it.

        Args:
            tag (Tag): Tag the user will be asked to provide
        
        Returns:
            Union[str, int]: Value entered by the user
        '''

        self._explain_set_tag(tag)
        self.tags[tag] = self._ask_tag(tag)

        return self.tags[tag]

    def _explain_set_tag(self, tag: Tag) -> None:
        logger.log(
            f'File [blue]{self.file}[/blue] '
            f'is missing its [green]{tag.name} tag[/green].'
        )
        logger.log(
            'Please provide it now. If no value is given, the file will be '
            f'placed in an [green]Unknown {tag.name}[/green] folder'
        )

    def _ask_tag(self, tag: Tag) -> Optional[Union[str, int]]:
        done = False
        validated = None
        while not done:
            value = input(f'{tag.name}: ')
            value.strip()

            if value:
                try:
                    validated = Tag.validate_input(tag, value)
                    done = True
                except ValueError as e:
                    logger.error(str(e))

            else:
                # User chose not to provide a value
                done = True

        return validated

    def set_tags_from_file(self):
        '''
        Set the tags from the file's metadata.
        '''
        tags = self._get_mutagen_tags()
        self.tags = self._parse_mutagen_tags(tags)

    def _get_mutagen_tags(self):
        try:
            return EasyID3(self.file)
        except ID3NoHeaderError:
            return MutagenFile(self.file)

    def _parse_mutagen_tags(self, mutagen_tags):
        return {
            tag: (
                mutagen_tags[tag.value][0] if tag.value in mutagen_tags
                else None
            )
            for tag in Tag
        }

    def save_tags(
        self,
        verbose: bool = False,
        dry_run: bool = False
    ):
        '''
        Saves the current tag values to the file.

        Args:
            verbose (bool): If True, each tag saving will be displayed.
            dry_run (bool): If True, the tags won't actually be saved, but the
                would-be modifications are displayed.
        '''

        mutagen_tags = self._get_mutagen_tags()
        old_tags = self._parse_mutagen_tags(mutagen_tags)

        for tag in Tag:
            old = old_tags[tag]
            new = self.tags[tag]

            if old != new:
                message = [
                    f'File [blue]{self.file}[/blue]:',
                    f'Overriding old {tag.name} tag value '
                    f'[red]{old}[/red]',
                    f'with [green]{new}[/green]'
                ]
                if dry_run:
                    logger.dry_run(message)
                elif verbose:
                    logger.info(message)

                mutagen_tags[tag.value] = new

        if not dry_run:
            mutagen_tags.save()

    def build_file_name(self, formatted_string: FormattedString) -> str:
        '''
        Builds the file's whole name, using the given format,
        and appends the extension.
        '''
        from .os_utils import file_extension  # Avoid circular import
        return formatted_string.build(self.tags) + file_extension(self.file)
