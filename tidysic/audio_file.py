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

    accept_all_guesses = False

    def __init__(self, file):
        self.file = file
        self.tags = self.read_tags()

    def guess_tags(self, dry_run):
        '''
        Guess the artist and title based on the filename
        '''
        from .os_utils import filename  # Avoid circular import
        name = filename(self.file, with_extension=False)
        try:
            # Artist and title are often seprated by ' - '
            separator = name.find(' - ')
            if separator > 0:
                artist = name[0:separator].lstrip()
                title = name[separator + 2:len(name)].lstrip()
                new_tags = {
                    Tag.Artist: name[0:separator].lstrip(),
                    Tag.Title: name[separator + 2:len(name)].lstrip()
                }

                if AudioFile.accept_all_guesses:
                    self.save_tags(new_tags, dry_run)
                else:
                    # Ask user what to do
                    logger.log([
                        f'''Guessed [blue]{artist}[/blue], \
[yellow]{title}[/yellow]''',
                        'Accept (y)',
                        'Accept all (a)',
                        'Discard (d)',
                        'Rename (r)'
                    ])

                    answer = input('(y/a/d/r) ? ')
                    while answer not in ['y', 'a', 'd', 'r']:
                        logger.log('Answer not understood')
                        answer = input('(y/a/d/r) ? ')

                    if answer == 'd':  # Discard
                        return

                    if answer == 'a':  # Accept all
                        AudioFile.accept_all_guesses = True

                    elif answer == 'r':  # Manual naming
                        new_tags[Tag.Title] = input('Title : ')
                        new_tags[Tag.Artist] = input('Artist : ')

                    self.save_tags(new_tags, dry_run)

            else:
                # If nothing is guessed, ask user what to do
                logger.log([
                    f'Cannot guess artist and/or title for {self.file}',
                    'Rename manually (r)',
                    'Discard (d)'
                ])

                answer = input('(r/d) ? ')
                while answer not in ['d', 'r']:
                    logger.log('Answer not understood')
                    answer = input('(r/d) ? ')

                if answer == 'r':
                    new_tags = {}
                    new_tags[Tag.Title] = input('Title : ')
                    new_tags[Tag.Artist] = input('Artist : ')

                    self.save_tags(new_tags, dry_run)

        except BaseException:
            logger.warning(f'Could not parse the title: {title}')

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
