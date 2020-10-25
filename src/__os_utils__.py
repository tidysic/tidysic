import os
import shutil
from __logger__ import log


audio_extensions = [
    '.mp3',
    '.wav',
    '.flac',
    '.ogg',
]


def _log_dry_run(message):
    log(message, prefix="dry run")


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
        # We don't display the two whole paths
        # Only the source's filename and the target directory
        src = file.split("/")[-1]
        target = "/".join(target_path.split("/")[:-1])
        
        _log_dry_run([
            "Moving file",
            f"'{src}'",
            "to",
            target
        ])
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
