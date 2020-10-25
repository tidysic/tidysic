#!/usr/local/bin/python3

import os
import shutil
from tinytag import TinyTag
from __argparse__ import create_parser

audio_extensions = [
    '.mp3',
    '.wav',
]


def filename(path):
    '''
    Returns the name of the file from the given path.
    '''
    return os.path.basename(path)


def file_extension(path):
    '''
    Returns the file extension from the given path.
    '''
    return os.path.splitext(path)[1]


def create_dir(dir_path):
    '''
    Creates the given directory if it does not exist yet.
    '''
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_audio_files(directory_path):
    '''
    Returns the audio files present in the given directory.
    '''
    audio_files = [os.path.join(directory_path, f) for f in os.listdir(
        directory_path) if os.path.splitext(f)[1] in audio_extensions]
    return audio_files


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


def parse_in_directory(dir_src):
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
        album = tag.album
        title = tag.title
        '''
        if not artist:
            try:
                guessed = guess_artist(title)
                artist = guessed[0]
                title = guessed[1]
            except:
                print_error('Could not guess artist: {0}'.format(title))
        '''

        if artist not in artists:
            artists[artist] = {}
        
        albums = artists[artist]
        if album not in albums:
            albums[album] = {}
        
        titles = albums[album]
        titles[title] = f


def move_files(artists, dir_target):
    for artist in artists.keys:
        # Directory name of the file based on the target directory and the
        # artist
        artist_dir_name = os.path.join(dir_target, artist)
        create_dir(artist_dir_name)

        for album in artist:
            # Subdirectory for the album
            album_dir_name = os.path.join(artist_dir_name, album)
            create_dir(album_dir_name)

            for title in album:
                # Rename the file
                f_name = title.join(file_extension(f))
                f_target_path = os.path.join(album_dir_name, f_name)

                # Moves the file to its new path
                try:
                    # shutil.move(f, f_target_path)
                    shutil.copyfile(f, f_target_path)
                except BaseException:
                    print_error(f'Could not move the file: {filename(f)}')


def clean_up(dir_src):
    '''
    TODO: remove empty folders in the source directory
    if the dry_run argument wasn't given
    '''
    pass


def organise(dir_src, dir_target):
    artists = parse_in_directory(dir_src)
    
    move_files(artists, dir_target)

    clean_up(dir_src)


def project_root_folder():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_src_folder():
    return os.path.join(project_root_folder(), 'src')


def project_test_folder():
    return os.path.join(project_root_folder(), 'test')


def lint_folders():
    return [project_src_folder(), project_test_folder()]


if __name__ == '__main__':

    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        print("tidysic v0.01")
        exit()
    elif args.command == 'organize':
        print(f"Beginning organizing {args.source} into {args.target}")
        # organise(
        #     args.source,
        #     args.target,
        #     args.dry_run
        #     )
    elif args.command == 'lint':
        folders = lint_folders()
        os.system(f'flake8 {folders[0]} {folders[1]}')
    elif args.command == 'lintfix':
        folders = lint_folders()
        os.system(
            f'autopep8 --in-place --recursive {folders[0]} {folders[1]}')
    else:
        parser.print_usage()
