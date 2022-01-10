from enum import IntEnum
from typing import Iterable, TypeAlias

from rich.console import Console
from rich.progress import ProgressType
from rich.progress import track as rich_track
from rich.text import Text as Text  # Explicit re-export
from rich.theme import Theme


class LogLevel(IntEnum):

    INFO = 1
    WARN = 2
    ERROR = 3
    NONE = 4


String: TypeAlias = str | Text
Message: TypeAlias = list[String] | String

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


def track(
    sequence: Iterable[ProgressType], description: str, transient: bool
) -> Iterable[ProgressType]:
    """
    Wrapper for the track method using the correct console.
    """

    yield from rich_track(
        sequence, description=description, transient=transient, console=_stdout
    )


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

    lines: list[String] = message if isinstance(message, list) else [message]

    text.append(lines[0])
    for line in lines[1:]:
        text.append("\n\t")
        text.append(line)

    console.print(text)
