from typing import Union

from rich import print


def log(
    message: Union[str, list[str]],
    prefix: str = '',
    color: str = 'blue'
):
    '''
    Log messages in the terminal.

    Args:
        message: String or list of strings which is printed on multiple lines.
        prefix (str): adds a short text before the message.
        color (str): changes the color of the prefix. Must be compatible with
            `rich`.
    '''

    if len(prefix) > 0:
        prefix = f' [italic]{prefix}[/italic]'

    prefix = ''.join([f'[{color}]', '\[tidydic]', prefix, f'[/{color}]: '])

    # create a multi-line message if we received a list
    if isinstance(message, list):
        message = '\n' + '\n'.join([f'\t{line}' for line in message])

    print(prefix + message)


def error(message: Union[str, list[str]]):
    log(message, prefix='Error', color='red')


def warning(message: Union[str, list[str]]):
    log(message, prefix='Warning', color='orange1')


def info(message: Union[str, list[str]]):
    log(message, prefix='Info')


def dry_run(message: Union[str, list[str]]):
    '''
    Shortcut to call logger with specific 'dry run' prefix.
    '''
    log(message, prefix='dry run')
