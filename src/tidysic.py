#!/usr/local/bin/python3

from tinytag import TinyTag
import eyed3
import os
from __argparse__ import create_parser
from __os_utils__ import (file_extension, filename,
                          create_dir, get_audio_files, move_file, lint_folders)
from __logger__ import log


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

            return (artist, title)
        return (None, None)
    except BaseException:
        print_error(f'Could not parse the title: {title}')


def print_error(message):
    log(message, prefix="Error", color="red")


def parse_in_directory(dir_src, with_album, guess):
    '''
    Creates a tree-like structure of dicts structured as such:
    artists -> albums -> titles
    where each of these is a dict, and titles point to the files themselves
    '''
    artists = {}
    audio_files = get_audio_files(dir_src)

    for f in audio_files:
        tag = TinyTag.get(f)
        artist = tag.artist
        title = tag.title

        if guess and not artist or not title:
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
            print(f'Could not move the file: {f}')

    return artists


def move_files(artists, dir_target, with_album, dry_run=False):
    for artist, second_level in artists.items():
        # Directory name of the file based on the target directory and the
        # artist
        artist_dir_name = os.path.join(dir_target, artist)

        create_dir(artist_dir_name, dry_run)

        if with_album:
            for album, titles in second_level.items():
                # Subdirectory for the album
                album_dir_name = os.path.join(artist_dir_name, album)
                create_dir(album_dir_name, dry_run)

                for title, file in titles.items():
                    # Rename the file
                    f_name = title + file_extension(file)
                    f_target_path = os.path.join(album_dir_name, f_name)

                    # Moves the file to its new path
                    move_file(file, f_target_path, dry_run)
        else:
            for title, file in second_level.items():
                # Rename the file
                f_name = title + file_extension(file)
                f_target_path = os.path.join(artist_dir_name, f_name)

                # Moves the file to its new path
                move_file(file, f_target_path, dry_run)


def clean_up(dir_src, dry_run=False):
    '''
    TODO: remove empty folders in the source directory
    if the dry_run argument wasn't given
    '''
    pass


def organise(dir_src, dir_target, with_album, guess, dry_run):
    artists = parse_in_directory(dir_src, with_album, guess)

    move_files(artists, dir_target, with_album, dry_run)

    clean_up(dir_src, dry_run)


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        log("v0.01", prefix="Version")
        exit()
    elif args.command == 'organize':
        if args.verbose:
            log(
                f"Beginning organizing {args.source} into {args.target}",
                prefix="verbose",
                color="green"
            )
        organise(
            args.source,
            args.target,
            args.with_album,
            args.guess,
            args.dry_run
        )
    elif args.command == 'lint':
        folders = lint_folders()
        os.system(f'flake8 {folders[0]} {folders[1]}')
    elif args.command == 'lintfix':
        folders = lint_folders()
        os.system(
            f'autopep8 --in-place --recursive {folders[0]} {folders[1]}')
    else:
        parser.print_usage()
