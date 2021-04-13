import os
import shutil
from typing import Union

from tidysic import logger

audio_extensions = {
    '.mp3',
    '.wav',
    '.flac',
    '.ogg',
}


def filename(
    path: str,
    with_extension: bool = True
) -> str:
    '''
    Returns the name of the file from `path` with or without the extension.
    '''
    name = os.path.basename(path)
    return name if with_extension else os.path.splitext(name)[0]


def file_extension(
    path: str
) -> str:
    '''
    Returns the file extension from `path`.
    '''
    return os.path.splitext(path)[1]


def is_audio_file(
    path: str
) -> bool:
    '''
    Returns whether the given file is an audio file.

    Args:
        path (str): File to test

    Returns:
        bool: True if the given file is an audio file
    '''
    return (
        os.path.isfile(path)
        and
        file_extension(path) in audio_extensions
    )


def create_dir(
    dir_name: str,
    parent_path: str,
    dry_run: bool,
    verbose: bool
) -> str:
    '''
    Creates the directroy `dir_name` in `parent_path`.
    '''
    dir_name = dir_name.replace('/', '-')
    full_path = os.path.join(parent_path, dir_name)

    _message(f'Create directory {full_path}', dry_run, verbose)
    if not dry_run:
        os.makedirs(full_path, exist_ok=True)

    return full_path


def move_file(
    file: str,
    target_name: str,
    target_path: str,
    dry_run: bool,
    verbose: bool
):
    '''
    Moves `file` to `target_path`, eventually renaming it `target_name`.
    '''
    target_name = target_name.replace('/', '-')
    full_path = os.path.join(target_path, target_name)

    _message(
        [
            'Moving file',
            f'{filename(file)}',
            'to',
            full_path
        ],
        dry_run,
        verbose
    )

    if not dry_run:
        shutil.move(file, full_path)


def remove_file(
    file_path: str,
    dry_run: bool,
    verbose: bool
):
    '''
    Deletes `file_path`
    '''
    _message(f"Deleting file {file_path}", dry_run, verbose)

    if not dry_run:
        os.remove(file_path)


def remove_directory(
    dir_path: str,
    verbose: bool
):
    '''
    Deletes `dir_path`.
    '''
    try:
        os.rmdir(dir_path)
        if verbose:
            logger.info(f'Deleting directory {dir_path}')
    except OSError:
        pass


def _message(
    message: Union[str, list[str]],
    dry_run: bool,
    verbose: bool
):
    '''
    Shortcut for calling the logger using the correct method.
    '''
    if dry_run:
        logger.dry_run(message)
    elif verbose:
        logger.info(message)


def project_root_folder():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def project_src_folder():
    return os.path.join(project_root_folder(), 'src')


def project_test_folder():
    return os.path.join(project_root_folder(), 'test')


def lint_folders():
    return [project_src_folder(), project_test_folder()]
