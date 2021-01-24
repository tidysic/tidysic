import argparse
import os


class PathType(object):
    '''
    Custom type we will use for folders, courtesy of
    https://stackoverflow.com/questions/11415570/directory-path-types-with-argparse#11415816
    '''

    def __init__(self, exists=True, type='file', dash_ok=True):
        '''exists:
                True: a path that does exist
                False: a path that does not exist, in a valid parent directory
                None: don't care
           type: file, dir, symlink, None, or a function returning True
                 for valid paths
                None: don't care
           dash_ok: whether to allow '-' as stdin/stdout'''

        assert exists in (True, False, None)
        assert type in (
            'file',
            'dir',
            'symlink',
            None) or hasattr(
            type,
            '__call__')

        self._exists = exists
        self._type = type
        self._dash_ok = dash_ok

    def __call__(self, string):
        if string == '-':
            # the special argument '-' means sys.std{in,out}
            if self._type == 'dir':
                raise argparse.ArgumentTypeError(
                    'standard input/output (-) not allowed as directory path')
            elif self._type == 'symlink':
                raise argparse.ArgumentTypeError(
                    'standard input/output (-) not allowed as symlink path')
            elif not self._dash_ok:
                raise argparse.ArgumentTypeError(
                    'standard input/output (-) not allowed')
        else:
            e = os.path.exists(string)
            if self._exists:
                if not e:
                    raise argparse.ArgumentTypeError(
                        f'path does not exist: {string}'
                    )

                if self._type is None:
                    pass
                elif self._type == 'file':
                    if not os.path.isfile(string):
                        raise argparse.ArgumentTypeError(
                            f'path is not a file: {string}'
                        )
                elif self._type == 'symlink':
                    if not os.path.symlink(string):
                        raise argparse.ArgumentTypeError(
                            f'path is not a symlink: {string}'
                        )
                elif self._type == 'dir':
                    if not os.path.isdir(string):
                        raise argparse.ArgumentTypeError(
                            f'path is not a directory: {string}'
                        )
                elif not self._type(string):
                    raise argparse.ArgumentTypeError(
                        f'path not valid: {string}'
                    )
            else:
                if self._exists is False and e:
                    raise argparse.ArgumentTypeError(
                        f'path exists: {string}'
                    )

                p = os.path.dirname(os.path.normpath(string)) or '.'
                if not os.path.isdir(p):
                    raise argparse.ArgumentTypeError(
                        f'parent path is not a directory: {p}'
                    )
                elif not os.path.exists(p):
                    raise argparse.ArgumentTypeError(
                        f'parent directory does not exist: {p}'
                    )

        return string


def create_parser():
    '''
    Creates the argument parser for the whole program
    '''
    parser = argparse.ArgumentParser(
        description='''
            organize your music files into folders
        ''',
        prog="tidysic"
    )

    parser.add_argument(
        '-V',
        '--version',
        help='show version',
        action='version',
        version='%(prog)s v0.1'
    )

    parser.add_argument(
        '-v',
        '--verbose',
        help='display more info when running',
        action='store_true',
    )

    parser.add_argument(
        '--with-album',
        help='''create an album directory inside the artist directory''',
        action='store_true',
    )

    parser.add_argument(
        '-g',
        '--guess',
        help='''\
            guess the audio file title and artist when there is no IDE tags''',
        action='store_true',
    )

    parser.add_argument(
        '-d',
        '--dry-run',
        help='''do nothing on the files themselves, but print out the \
            actions that would happen''',
        action='store_true',
        dest='dry_run',
    )

    parser.add_argument(
        'source',
        type=PathType(
            exists=True,
            type='dir',
            dash_ok=False
        ),
        help='directory whose content will be organized',
    )

    parser.add_argument(
        'target',
        type=PathType(
            exists=None,
            type='dir',
            dash_ok=False
        ),
        help='''directory (will be created if needed) in which the \
            files will be organized''',
    )

    return parser
