from tinytag import TinyTag
import eyed3
import os
from collections import namedtuple

from .tag import Tag, get_tags
from .os_utils import (file_extension, filename,
                       create_dir, get_audio_files, move_file)
from .logger import log


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
                    f"""Guessed [blue]{artist}[/blue], \
                        [yellow]{title}[/yellow]""",
                    "Accept (y)",
                    "Accept all (a)",
                    "Discard (d)",
                    "Rename (r)"
                    ])
                answer = input("(y/a/d/r) ? ")
                while answer not in ["y", "a", "d", "r"]:
                    log("Answer not understood")
                    answer = input("(y/a/d/r) ? ")
                # accept once
                if answer == "y":
                    return (artist, title)
                # accept all
                elif answer == "a":
                    guess_file_metadata.accept_all = True
                    return (artist, title)
                elif answer == "d":
                    return(None, None)
                elif answer == "r":
                    artist = input("Artist : ")
                    title = input("Title : ")
                    return(artist, title)
        else:
            # if nothing is guessed, ask user what to do
            log([
                "Can't guess artist and/or title. What do you want to do ?",
                "Rename manually (r)",
                "Discard (d)"
                ])
            answer = input("(r/d) ? ")
            while answer not in ["d", "r"]:
                log("Answer not understood")
                answer = input("(r/d) ? ")
            # accept once
            if answer == "d":
                return(None, None)
            elif answer == "r":
                artist = input("Artist : ")
                title = input("Title : ")
                return(artist, title)
    except BaseException:
        print_error(f'Could not parse the title: {title}')


guess_file_metadata.accept_all = False


def print_error(message):
    log(message, prefix='Error', color='red')


def create_structure(files: list, structure: list, guess: bool):
    '''
    Given a list of files and a tag type, creates a StructureLevel object.

    It consists of a pair whose first element is a dict whose keys
    are the values of the tag that were found in the files,
    and whose values are lists of files.

    The second element of the pair is a list of all the files for
    which the tag was not found.
    '''
    ordered = {}
    unordered = []

    order_tag = structure[0]

    for file in files:

        tag = get_tags(file)[order_tag]
        if tag is None:
            if order_tag in [Tag.Artist, Tag.Title]:
                # TODO call guess_metadata
                pass
            else:
                unordered.append(file)
        else:
            if tag not in ordered:
                ordered[tag] = []
            ordered[tag].append(file)

    if len(structure) > 1:
        for tag_value, files in ordered.items():
            ordered[tag_value] = create_structure(
                files,
                structure[1:],
                guess
            )

    return StructureLevel(ordered, unordered)


def parse_in_directory(dir_src, structure, guess, verbose):
    '''
    Creates a tree-like structure whose nodes are StructureLevel objects.

    The depths of the tree coincide with the structure passed as argument.
    For instance, if the structure given is `[Tag.Artist, Tag.Title]`, the root
    of the structure will be a dict of artists.
    '''
    audio_files = get_audio_files(dir_src)

    root = create_structure(audio_files, structure, guess)

    return root


            # Save the id3 tags
            audiofile.tag.save()

        if artist and title:
            # Add artist key
            if artist not in artists:
                artists[artist] = {}

            if with_album:
                album = tag.album
                albums = artists[artist]

                # Add album key
                if album not in albums:
                    albums[album] = {}

                titles = albums[album]
                titles[title] = f
            else:
                artists[artist][title] = f
        else:
            if verbose:
                log("file discarded", prefix="warn", color="red")

    return artists



def move_files(
    files: StructureLevel,
    dir_target: str,
    structure: list,
    dry_run=False,
):
    for file in files.unordered:
        file_name = filename(file)
        file_path = os.path.join(dir_target, file_name)
        move_file(file, file_path, dry_run)

    for tag, content in files.ordered.items():

        dir_name = os.path.join(dir_target, tag)
        create_dir(dir_name, dry_run)

        if isinstance(content, list):  # Leaf of the structure tree
            file = content[0]
            tag = structure[0]

            file_name = str(tag) + file_extension(file)
            file_path = os.path.join(dir_target, file_name)
            move_file(file, file_path, dry_run)
        else:
            move_files(
                content,
                dir_name,
                structure[:1],
                dry_run
            )


def clean_up(dir_src, dry_run=False):
    '''
    TODO: remove empty folders in the source directory
    if the dry_run argument wasn't given
    '''
    pass


def organise(dir_src, dir_target, with_album, guess, dry_run, verbose):

    structure = [Tag.Artist]
    if with_album:
        structure.append(Tag.Album)
    structure.append(Tag.Title)

    root = parse_in_directory(
        dir_src,
        structure,
        guess,
        verbose
    )

    move_files(
        root,
        dir_target,
        structure,
        dry_run
    )

    clean_up(dir_src, dry_run)
