import eyed3

from .tag import Tag, get_tags
from .logger import log, warning, dry_run as log_dry_run


class AudioFile(object):

    accept_all_guesses = False

    def __init__(self, file):

        self.file = file
        self.tags = get_tags(file)
        self.guessed_tags = None

    def guess_tags(self, dry_run):
        '''
        Guess the artist and title based on the filename
        '''
        from .os_utils import filename
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

            tags_wrapper = eyed3.load(self.file)
            # TODO: Make this more generic if other tags
            # than artist and title can be guessed later on
            if Tag.Title in new_tags:
                tags_wrapper.tag.title = new_tags[Tag.Title]
            if Tag.Artist in new_tags:
                tags_wrapper.tag.artist = new_tags[Tag.Artist]
            tags_wrapper.tag.save()

    def build_file_name(self, format: str):
        from .os_utils import file_extension  # Avoid circular import
        return format.format(
            title=self.tags[Tag.Title],
            album=self.tags[Tag.Album],
            artist=self.tags[Tag.Artist],
            year=self.tags[Tag.Year],
            track=int(self.tags[Tag.Track]),
            genre=self.tags[Tag.Genre]
        ) + file_extension(self.file)
