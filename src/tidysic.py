#!/usr/local/bin/python3

from tinytag import TinyTag
import os
from __argparse__ import create_parser
from __os_utils__ import *


def guess_artist(title):
    '''
    '''
    try:
        artist_separator = title.find('-')
        if artist_separator > 0:
            artist = title[0:artist_separator].lstrip()
            new_title = title[artist_separator + 1:-1].lstrip()

            return [artist, new_title]
    except BaseException:
        print_error('Could not parse the title: {0}'.format(title))


def print_error(message):
    print('--- Error ---')
    print(message)
    print()


def parse_in_directory(dir_src, with_album):
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

        if artist:
            # Add artist key
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
            print(f'Could not get artist: {title}')

    return artists


def move_files(artists, dir_target, with_album, dry_run=False):
    for artist in artists:
        # Directory name of the file based on the target directory and the
        # artist
        artist_dir_name = os.path.join(dir_target, artist)

        create_dir(artist_dir_name, dry_run)

        if with_album:
            for album in artists[artist]:
                # Subdirectory for the album
                album_dir_name = os.path.join(artist_dir_name, album)
                create_dir(album_dir_name, dry_run)

                for title in artists[artist][album]:
                    file = artists[artist][album][title]
                    # Rename the file
                    f_name = title + file_extension(file)
                    f_target_path = os.path.join(album_dir_name, f_name)

                    # Moves the file to its new path
                    move_file(file, f_target_path, dry_run)
        else:
            for title in artists[artist]:
                file = artists[artist][title]
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


def organise(dir_src, dir_target, with_album, dry_run):
    artists = parse_in_directory(dir_src, with_album)

    move_files(artists, dir_target, with_album, dry_run)

    clean_up(dir_src, dry_run)


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print("tidysic v0.01")
        exit()
    elif args.command == 'organize':
        print(f"Beginning organizing {args.source} into {args.target}")
        organise(
            args.source,
            args.target,
            args.with_album,
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
