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
    Class describing a file, and its associated tags
    '''

    def __init__(self, file):
        self.file = file
        self.tags = self.read_tags()

    def ask_and_set_tag(self, tag: Tag):     
        '''
        Ask the user to provide one of the file's tags, and set it.

        Args:
            tag (Tag): Tag the user will be asked to provide

        Returns:
            Union[str, int]: Value entered by the user
        '''

        logger.log(
            f'File [blue]{self.file}[/blue] '
            f'is missing its [green]{tag.name} tag[/green].'
        )
        logger.log(
            'Please provide it now. If left blank, the file will be '
            f'placed in a [green]Unknown {tag.name}[/green] folder'
        )

        done = False
        while not done:
            value = input(f'{tag.name}: ')
            value.strip()

            if value:
                if tag in Tag.numeric_tags():
                    try:
                        self.tags[tag] = int(value)
                        done = True
                    except ValueError:
                        pass

            else:
                    self.tags[tag] = value
                    done = True

        return self.tags[tag]

    def read_tags(self):
        '''
        Reads the tags from the file's metadata
        '''
        tags = None
        try:
            tags = EasyID3(self.file)
        except ID3NoHeaderError:
            tags = MutagenFile(self.file)

        return {
            tag: tags[tag.value][0] if tag.value in tags else None
            for tag in Tag
        }

    def save_tags(self, new_tags, dry_run):
        '''
        Applies the given collection of tags to itself and
        saves them to the file (if `dry_run == True`)
        '''
        for tag, value in new_tags.items():
            self.tags[tag] = value

        if dry_run:
            message = ['Saving tags into file:']
            message += [
                f'{str(tag)} : {value}'
                for tag, value in new_tags.items()
            ]
            logger.dry_run(message)

        else:
            for tag, value in new_tags.items():
                self.tags[tag] = value

            tags = None
            try:
                tags = EasyID3(self.file)
            except ID3NoHeaderError:
                tags = MutagenFile(self.file)

            for tag, value in new_tags.items():
                tags[tag.value] = value
            tags.save()

    def build_file_name(self, formatted_string: FormattedString):
        '''
        Builds the file's whole name, using the given format,
        and appends the extension.
        '''
        from .os_utils import file_extension  # Avoid circular import
        return formatted_string.build(self.tags) + file_extension(self.file)
