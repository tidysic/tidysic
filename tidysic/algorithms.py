import eyed3
import os
from collections import namedtuple

from .tag import Tag
from .os_utils import (file_extension, filename,
                       create_dir, get_audio_files, move_file,
                       remove_directory)
from .logger import log, error, warning


StructureLevel = namedtuple(
    'StructureLevel',
    ['ordered', 'unordered']
)


def guess_file_metadata(filename):
    '''
    Guess the artist and title based on the filename
    '''
    try:
        # Artist and title are often seprated by ' - '
        separator = filename.find(' - ')
        if separator > 0:
            artist = filename[0:separator].lstrip()
            title = filename[separator + 2:len(filename)].lstrip()

            if guess_file_metadata.accept_all:
                return (artist, title)
            else:
                # ask user what to do
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
                # accept once
                if answer == 'y':
                    return (artist, title)
                # accept all
                elif answer == 'a':
                    guess_file_metadata.accept_all = True
                    return (artist, title)
                elif answer == 'd':
                    return (None, None)
                elif answer == 'r':
                    artist = input('Artist : ')
                    title = input('Title : ')
                    return (artist, title)
        else:
            # if nothing is guessed, ask user what to do
            log([
                'Cannot guess artist and/or title. What do you want to do ?',
                'Rename manually (r)',
                'Discard (d)'
            ])
            answer = input('(r/d) ? ')
            while answer not in ['d', 'r']:
                log('Answer not understood')
                answer = input('(r/d) ? ')
            # accept once
            if answer == 'd':
                return (None, None)
            elif answer == 'r':
                artist = input('Artist : ')
                title = input('Title : ')
                return (artist, title)

    except BaseException:
        error(f'Could not parse the title: {title}')


guess_file_metadata.accept_all = False


def apply_guessing(file, order_tag, dry_run):
    '''
    Runs the `guess_file_metadata` and applies the result
    to the file.
    '''
    guessed_artist, guessed_title = guess_file_metadata(
        filename(file, with_extension=False))

    audiofile = eyed3.load(file)

    if order_tag == Tag.Artist and guessed_artist:
        if not dry_run:
            audiofile.tag.artist = guessed_artist
            audiofile.tag.save()
        return guessed_artist
    elif guessed_title:
        if not dry_run:
            audiofile.tag.title = guessed_title
            audiofile.tag.save()
        return guessed_title
    else:
        return None


def create_structure(
    audio_files: list,
    structure: list,
    guess: bool,
    dry_run: bool
):
    '''
    Given a list of AudioFiles and a tag type, creates a StructureLevel object.

    It consists of a pair whose first element is a dict whose keys
    are the values of the tag that were found in the files,
    and whose values are lists of files.

    The second element of the pair is a list of all the files for
    which the tag was not found.
    '''
    ordered = {}
    unordered = []

    order_tag = structure[0]

    for file in audio_files:

        tag = file.tags[order_tag]
        if tag is None:
            if order_tag in [Tag.Artist, Tag.Title] and guess:
                file.guess_tags(dry_run)
                tag = file.tags[order_tag]

                if tag is None:
                    log(f'Discarded file: {file}')
            else:
                # Default behavior is letting the file in the
                # lowest folder we can.
                warning(f'''\
                    File {file}
                    could not have its {str(order_tag)} tag determined.
                    It will stay in the parent folder.\
                ''')
                unordered.append(file)

        if tag is not None:
            if tag not in ordered:
                ordered[tag] = []
            ordered[tag].append(file)

    if len(structure) > 1:
        for tag_value, files in ordered.items():
            ordered[tag_value] = create_structure(
                files,
                structure[1:],
                guess,
                dry_run
            )

    return StructureLevel(ordered, unordered)


def parse_in_directory(audio_files, structure, guess, verbose, dry_run):
    '''
    Creates a tree-like structure whose nodes are StructureLevel objects.

    The depths of the tree coincide with the structure passed as argument.
    For instance, if the structure given is `[Tag.Artist, Tag.Title]`, the root
    of the structure will be a dict of artists.
    '''
    root = create_structure(audio_files, structure, guess, dry_run)

    return root


def move_files(
    audio_files: StructureLevel,
    dir_target: str,
    structure: list,
    format: str,
    dry_run=False,
):
    '''
    Moves the given files into a folder hierarchy following
    the given structure.
    '''
    for file in audio_files.unordered:
        file_name = file.build_file_name(format)
        file_path = os.path.join(dir_target, file_name)
        move_file(file.file, file_path, dry_run)

    for tag, content in audio_files.ordered.items():

        if isinstance(content, list):  # Leaf of the structure tree
            for audio_file in content:
                file_name = audio_file.build_file_name(format)
                file_path = os.path.join(dir_target, file_name)
                move_file(audio_file.file, file_path, dry_run)
        else:

            dir_name = os.path.join(dir_target, tag)
            create_dir(dir_name, dry_run)

            move_files(
                content,
                dir_name,
                structure[:1],
                format,
                dry_run
            )


def clean_up(dir_src, audio_files, dry_run=False):
    if not os.path.isdir(dir_src):
        return

    # remove empty subfolders
    files = os.listdir(dir_src)
    if len(files):
        for f in files:
            fullpath = os.path.join(dir_src, f)
            if os.path.isdir(fullpath):
                clean_up(fullpath, audio_files, dry_run)

    # if folder empty, delete it
    files = os.listdir(dir_src)
    if not any([
        file in [
            audio_file.file
            for audio_file in audio_files
        ]
        for file in files
    ]):
        remove_directory(dir_src, dry_run)


def organize(dir_src, dir_target, with_album, guess, dry_run, verbose):
    '''
    Concisely runs the three parts of the algorithm.
    '''

    structure = [Tag.Artist]
    if with_album:
        structure += [Tag.Album]

    audio_files = get_audio_files(dir_src)

    root = parse_in_directory(
        audio_files,
        structure,
        guess,
        verbose,
        dry_run
    )

    format = '{track:02}) {title}'
    move_files(
        root,
        dir_target,
        structure,
        format,
        dry_run
    )

    clean_up(dir_src, audio_files, dry_run)
