from tinytag import TinyTag
import eyed3
import os

from .os_utils import (file_extension, filename,
                       create_dir, get_audio_files, move_file,
                       remove_directory)
from .logger import log, error, warning


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
        error(f'Could not parse the title: {title}')


guess_file_metadata.accept_all = False


def parse_in_directory(audio_files, with_album, guess, verbose):
    '''
    Creates a tree-like structure of dicts structured as such:
    artists -> albums -> titles
    where each of these is a dict, and titles point to the files themselves
    '''
    artists = {}

    for f in audio_files:
        tag = TinyTag.get(f)
        artist = tag.artist
        title = tag.title

        if guess and (not artist or not title):
            # artist and/or title not in the id3 metadata
            guessed_artist, guessed_title = guess_file_metadata(
                filename(f, with_extension=False))
            audiofile = eyed3.load(f)
            if not artist and guessed_artist:
                artist = guessed_artist
                audiofile.tag.artist = artist
            if not title and guessed_title:
                title = guessed_title
                audiofile.tag.title = title

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
                warning("file discarded")

    return artists


def move_files(artists, dir_target, with_album, dry_run=False):
    for artist, second_level in artists.items():
        # Directory name of the file based on the
        # target directory and the artist
        artist_dir = create_dir(artist, dir_target, dry_run)

        if with_album:
            for album, titles in second_level.items():
                # Create album folder
                album_dir = create_dir(album, artist_dir, dry_run)

                for title, file in titles.items():
                    # Moves the file to its new path
                    move_file(file, title, album_dir, dry_run)
        else:
            for title, file in second_level.items():
                # Moves the file to its new path
                move_file(file, title, artist_dir, dry_run)


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
        file in audio_files
        for file in files
    ]):
        remove_directory(dir_src, dry_run)


def organise(dir_src, dir_target, with_album, guess, dry_run, verbose):
    audio_files = get_audio_files(dir_src)

    artists = parse_in_directory(audio_files, with_album, guess, verbose)

    move_files(artists, dir_target, with_album, dry_run)

    clean_up(dir_src, audio_files, dry_run)
