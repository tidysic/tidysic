from enum import IntEnum
from typing import Iterable

from rich.console import Console
from rich.progress import ProgressType
from rich.progress import track as rich_track
from rich.text import Text
from rich.theme import Theme


class LogLevel(IntEnum):

    INFO = 1
    WARN = 2
    ERROR = 3
    NONE = 4


String = str | Text
Message = String | list[String]

theme = Theme(
    {
        "info": "blue",
        "warning": "red",
        "error": "bold red",
        "path": "underline dim",
        "tag": "yellow",
        "config": "green",
    }
)

_log_level = LogLevel.WARN
_stdout = Console(theme=theme)
_stderr = Console(theme=theme, stderr=True)


def track(*args, **kwargs) -> Iterable[ProgressType]:
    """
    Wrapper for the track method using the correct console.
    """
    return rich_track(*args, **kwargs, console=_stdout)


def set_log_level(level: LogLevel) -> None:
    """
    Sets the highest level of logging that will be displayed.
    """
    global _log_level
    _log_level = level


def info(message: Message) -> None:
    """
    If the current log level permits it, displays useful information on the process.
    """
    if _log_level <= LogLevel.INFO:
        _log(message, prefix="info")


def warn(message: Message) -> None:
    """
    If the current log level permits it, displays non-fatal errors.
    """
    if _log_level <= LogLevel.WARN:
        _log(message, prefix="warning", console=_stderr)


def error(message: Message) -> None:
    """
    If the current log level permits it, displays fatal errors.
    """
    if _log_level <= LogLevel.ERROR:
        _log(message, prefix="error", console=_stderr)


def _log(
    message: Message,
    prefix: str | None,
    console: Console = _stdout,
) -> None:
    text = Text()

    if prefix is not None:
        text.append(f"[{prefix}] ", prefix)

    if isinstance(message, list):
        text.append(message[0])
        for line in message[1:]:
            text.append("\n\t")
            text.append(line)
    else:
        text.append(message)

    console.print(text)
