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


def organise(dir_src, dir_target):
    audio_files = get_audio_files(dir_src)
    for f in audio_files:
        tag = TinyTag.get(f)
        artist = tag.artist
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

        if artist:
            # Directory name of the file based on the target directory and the
            # artist
            f_dir_name = os.path.join(dir_target, artist)
            create_dir(f_dir_name)

            # New path for the file
            f_name = title.join(file_extension(f))
            f_target_path = os.path.join(f_dir_name, f_name)

            # Moves the file to its new path
            try:
                # shutil.move(f, f_target_path)
                shutil.copyfile(f, f_target_path)
            except BaseException:
                print_error('Could not move the file: {0}'.format(filename(f)))


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
        os.system('flake8 .')
    elif args.command == 'lintfix':
        os.system('autopep8 --in-place --recursive .')
