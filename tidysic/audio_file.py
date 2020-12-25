from mutagen import File as MutagenFile
import re

from .tag import Tag, get_tags
from .logger import log, warning, dry_run as log_dry_run


class AudioFile(object):
    '''
    Class describing a file, and its associated tags
    '''

    accept_all_guesses = False

    def __init__(self, file):
        self.file = file
        self.tags = get_tags(file)
        self.guessed_tags = None

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
                    log([
                        f'''Guessed [blue]{artist}[/blue], \
[yellow]{title}[/yellow]''',
                        'Accept (y)',
                        'Accept all (a)',
                        'Discard (d)',
                        'Rename (r)'
                    ])

                    answer = input('(y/a/d/r) ? ')
                    while answer not in ['y', 'a', 'd', 'r']:
                        log('Answer not understood')
                        answer = input('(y/a/d/r) ? ')

                    if answer == 'd':  # Discard
                        return

                    if answer == 'a':  # Accept all
                        AudioFile.accept_all_guesses = True

                    elif answer == 'r':  # Manual naming
                        new_tags[Tag.Title] = input('Title : ')
                        new_tags[Tag.Artist] = input('Artist : ')

                    self.save_tags(dry_run)

            else:
                # If nothing is guessed, ask user what to do
                log([
                    f'Cannot guess artist and/or title for {self.file}',
                    'Rename manually (r)',
                    'Discard (d)'
                ])

                answer = input('(r/d) ? ')
                while answer not in ['d', 'r']:
                    log('Answer not understood')
                    answer = input('(r/d) ? ')

                if answer == 'r':
                    new_tags[Tag.Title] = input('Title : ')
                    new_tags[Tag.Artist] = input('Artist : ')

                    self.save_tags(dry_run)

        except BaseException:
            warning(f'Could not parse the title: {title}')

    def save_tags(self, new_tags, dry_run):
        '''
        Applies the given collection of tags to itself and
        saves them to the file (if `dry_run == True`)
        '''
        if dry_run:
            message = ['Saving tags into file:']
            message += [
                f'{str(tag)} : {value}'
                for tag, value in new_tags.items()
            ]
            log_dry_run(message)

        else:
            for tag, value in new_tags.items():
                self.tags[tag] = value

            tags = MutagenFile(self.file)
            if tags:
                for tag, value in new_tags.items():
                    tags[tag.value] = value
                tags.save()

    def fill_formatted_str(self, format_str: str):
        '''
        Fills the given formatted string with the file's tags

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
        pattern = r'\{(.*?\{(\w+)(:.+?)?\}.*?)\}'
        matches = re.findall(pattern, format_str)

        substitutions = []
        for part, key, format_spec in matches:

            value = None
            for tag in Tag:
                if str(tag).lower() == key:
                    value = self.tags[tag]
                    if key in ['year', 'track'] and value:
                        value = int(value)

                    if key in ['title', 'artist', 'album'] and not value:
                        value = f'Unknown {key.capitalize()}'

                    break
            else:
                raise ValueError('%s is not a tag key' % key)

            formattable = part.replace(
                f'{{{key}{format_spec}}}',
                f'{{{format_spec}}}'
            )
            substitutions.append((
                f'{{{part}}}',
                formattable.format(value) if value else ''
            ))

        for old, new in substitutions:
            format_str = format_str.replace(old, new)

        return format_str

    def build_file_name(self, format_str: str):
        '''
        Builds the file's whole name, using the given tags and format,
        and appends the extension.
        '''
        from .os_utils import file_extension  # Avoid circular import

        return self.fill_formatted_str(format_str) + file_extension(self.file)
