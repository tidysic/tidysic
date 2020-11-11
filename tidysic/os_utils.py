import os
import shutil
from pathlib import Path

from tidysic import logger


audio_extensions = [
    '.mp3',
    '.wav',
    '.flac',
    '.ogg',
]


def filename(path, with_extension=True):
    '''
    Returns the name of the file from the given path
    with or without the extension.
    '''
    name = os.path.basename(path)

    if not with_extension:
        name = os.path.splitext(name)[0]

    return name


def file_extension(path):
    '''
    Returns the file extension from the given path.
    '''
    return os.path.splitext(path)[1]


def create_dir(dir_name, parent_path, dry_run):
    '''
    Creates a directory with the given name
    in the given parent directory
    '''
    dir_name = dir_name.replace('/', '-')
    full_path = os.path.join(parent_path, dir_name)
    if dry_run:
        logger.dry_run(f'Create directory {full_path}')
    elif not os.path.exists(full_path):
        os.makedirs(full_path)

    return full_path


def get_audio_files(directory_path):
    '''
    Returns the audio files present in the given directory.
    '''
    audio_files = [
        os.path.join(directory_path, path)
        for ext in audio_extensions
        for path in Path(directory_path).rglob('*'+ext)
    ]
    return audio_files


def move_file(file, target_name, target_path, dry_run=False):
    '''
    Moves the given file onto the given path
    '''
    target_name = target_name.replace('/', '-')
    target_name += file_extension(file)
    
    full_path = os.path.join(target_path, target_name)
    if dry_run:
        # We don't display the two whole paths
        # Only the source's filename and the target directory
        src = file.split('/')[-1]
        target = '/'.join(full_path.split('/')[:-1])

        logger.dry_run([
            'Moving file',
            f'{src}',
            'to',
            target
        ])
    else:
        shutil.move(file, full_path)


def remove_directory(dir_path, dry_run=False):
    '''
    Deletes the given directory
    '''
    if dry_run:
        logger.dry_run(f'Deleting directory {dir_path}')
    else:
        os.rmdir(dir_path)


def project_root_folder():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_src_folder():
    return os.path.join(project_root_folder(), 'src')


def project_test_folder():
    return os.path.join(project_root_folder(), 'test')


def lint_folders():
    return [project_src_folder(), project_test_folder()]
