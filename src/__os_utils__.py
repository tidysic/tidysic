import os
import shutil
from rich import print


audio_extensions = [
    '.mp3',
    '.wav',
    '.flac',
    '.ogg',
]


def _log_dry_run(message):
    print(f"[green]\[tidysic] [italic]dry run[/italic]:[/green] {message}")


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


def create_dir(dir_path, dry_run):
    '''
    Creates the given directory if it does not exist yet.
    '''
    if dry_run:
        _log_dry_run(f"Create directory {dir_path}")
    elif not os.path.exists(dir_path):
        os.makedirs(dir_path)


def get_audio_files(directory_path):
    '''
    Returns the audio files present in the given directory.
    '''
    audio_files = [os.path.join(directory_path, f) for f in os.listdir(
        directory_path) if os.path.splitext(f)[1] in audio_extensions]
    return audio_files


def move_file(file, target_path, dry_run=False):
    '''
    Moves the given file onto the given path
    '''
    if dry_run:
        _log_dry_run(
            f"Moving file {file} to its new path {target_path}"
        )
    else:
        shutil.move(file, target_path)


def remove_directory(dir_path, dry_run=False):
    '''
    Deletes the given directory
    '''
    if dry_run:
        _log_dry_run(f"Deleting directory {dir_path}")
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
