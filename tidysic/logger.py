from rich import print


def log(message, prefix='', color='blue'):
    '''
    Log messages in the terminal.
    The message can either be a string, or a list of strings,
    which will be printed on multiple lines.
    Prefix adds a short text before the message.
    Color changes the color of the prefix. Must be compatible with `rich`
    '''
    if len(prefix) > 0:
        prefix = f'[{color}]\[tidysic] [italic]{prefix}[/italic][/{color}]: '
    else:
        prefix = f'[{color}]\[tidysic][/{color}]: '

    if isinstance(message, str):
        print(prefix + message)
    else:
        print(prefix)
        for line in message:
            print('\t' + line)


def error(message):
    log(message, prefix='Error', color='red')


def warning(message):
    log(message, prefix='Warning', color='orange1')


def _log_dry_run(message):
    '''
    Shortcut to call logger with specific 'dry run' prefix
    '''
    log(message, prefix='dry run')
