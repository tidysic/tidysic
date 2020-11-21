import os
from collections import namedtuple
from typing import List

from .tag import Tag
from .audio_file import AudioFile
from .os_utils import (
    create_dir,
    get_audio_files,
    move_file,
    remove_directory
)
from .logger import log, warning


StructureLevel = namedtuple(
    'StructureLevel',
    ['ordered', 'unordered']
)


def create_structure(
    audio_files: List[AudioFile],
    ordering: List[Tag],
    guess: bool,
    dry_run: bool
):
    '''
    Given a list of AudioFiles and an ordering,
    creates a StructureLevel object.

    It consists of a pair whose first element is a dict whose keys
    are the values of the tag that were found in the files,
    and whose values are lists of AudioFiles or further StructureLevel.

    The second element of the pair is a list of all the AudioFiles
    for which the tag was not found.
    '''
    ordered = {}
    unordered = []

    assert(len(ordering) > 0)  # No structure without ordering

    order_tag = ordering[0]

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
                warning(f'''
File {file.file}
could not have its {str(order_tag)} tag determined.
It will stay in the parent folder.\
                ''')
                unordered.append(file)

        if tag is not None:
            if tag not in ordered:
                ordered[tag] = []
            ordered[tag].append(file)

    if len(ordering) > 1:
        for tag_value, files in ordered.items():
            ordered[tag_value] = create_structure(
                files,
                ordering[1:],
                guess,
                dry_run
            )

    return StructureLevel(ordered, unordered)


def move_files(
    audio_files: StructureLevel,
    dir_target: str,
    format: str,
    dry_run=False,
):
    '''
    Moves the given files into a folder hierarchy following
    the given structure.
    '''
    for file in audio_files.unordered:
        move_file(
            file.file,
            file.build_file_name(format),
            dir_target,
            dry_run
        )

    for tag, content in audio_files.ordered.items():
        sub_dir_target = create_dir(tag, dir_target, dry_run, False)

        if isinstance(content, list):  # Leaf of the structure tree
            for audio_file in content:
                move_file(
                    audio_file.file,
                    audio_file.build_file_name(format),
                    sub_dir_target,
                    dry_run,
                    False
                )

        else:
            move_files(
                content,
                sub_dir_target,
                format,
                dry_run
            )


def clean_up(
    dir_src: str,
    audio_files: List[AudioFile],
    dry_run: bool
):
    '''
    Remove empty folders in the source directory.
    '''
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
    if all([
        file in [
            audio_file.file
            for audio_file in audio_files
        ]
        for file in files
    ]):
        remove_directory(dir_src, dry_run, False)


def organize(
    dir_src: str,
    dir_target: str,
    with_album: bool,
    guess: bool,
    dry_run: bool,
    verbose: bool
):
    '''
    Concisely runs the three parts of the algorithm.
    '''

    structure = [Tag.Artist]
    if with_album:
        structure += [Tag.Album]

    audio_files = get_audio_files(dir_src)

    root = create_structure(
        audio_files,
        structure,
        guess,
        dry_run
    )

    format = '{title}'
    move_files(
        root,
        dir_target,
        format,
        dry_run
    )

    clean_up(dir_src, audio_files, dry_run)
