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


class Logger:

    _instance: "Logger" = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)

        return cls._instance

    def __init__(self):
        self._level = LogLevel.WARN
        self._stdout = Console(theme=theme)
        self._stderr = Console(theme=theme, stderr=True)

    def _set_loglevel(self, log_level: LogLevel) -> None:
        self._level = log_level

    level = property(fset=_set_loglevel)

    def track(
        self, sequence: Iterable[ProgressType], description: str, transient: bool
    ) -> Iterable[ProgressType]:
        """
        Wrapper for the track method using the correct console.
        """
        yield from rich_track(
            sequence, description=description, transient=transient, console=self._stdout
        )

    def info(self, message: Message) -> None:
        """
        If the current log level permits it, displays useful information on the process.
        """
        if self._level <= LogLevel.INFO:
            self._log(message, prefix="info")

    def warn(self, message: Message) -> None:
        """
        If the current log level permits it, displays non-fatal errors.
        """
        if self._level <= LogLevel.WARN:
            self._log(message, prefix="warning", console=self._stderr)

    def error(self, message: Message) -> None:
        """
        If the current log level permits it, displays fatal errors.
        """
        if self._level <= LogLevel.ERROR:
            self._log(message, prefix="error", console=self._stderr)

    def _log(
        self,
        message: Message,
        prefix: str | None,
        console: Console | None = None,
    ) -> None:
        text = Text()

        console = console or self._stdout

        if prefix is not None:
            text.append(f"[{prefix}] ", prefix)

        lines: list[String] = message if isinstance(message, list) else [message]

        text.append(lines[0])
        for line in lines[1:]:
            text.append("\n\t")
            text.append(line)

        console.print(text)
