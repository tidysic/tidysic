from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Callable

from tidysic.file.taggable import Taggable
from tidysic.file.tagged_file import TaggedFile
from tidysic.logger import Logger, Message, String, Text

log = Logger()


class TidysicException(Exception, ABC):
    @abstractmethod
    def get_error_message(self) -> Message:
        """
        Returns an error message friendly to the logger module.
        """
        ...


class CollisionException(TidysicException):
    """
    Exception raised when two or more files are to be moved or copied to the same
    target.
    """

    def __init__(self, files: list[TaggedFile], target: Path):
        self.files = files
        self.target = target

    def get_error_message(self) -> Message:
        message: list[String] = []
        message.append(
            Text.assemble(
                "more than one file have the same target: ",
                (str(self.target), "path"),
            )
        )
        message.append("They are the following:")
        for file in self.files:
            message.append(Text(str(file.path), "path"))
        message.append(
            "Consider adapting the structure using different tags to"
            " differentiate them."
        )
        return message


class EmptyStringException(TidysicException):
    """
    Exception raised when a formatted strings results in an empty string.
    """

    def __init__(self, raw_formatted_string: str, taggable: Taggable):
        self.raw_formatted_string = raw_formatted_string
        self.taggable = taggable

    def get_error_message(self) -> Message:
        message: list[String] = []
        message.append(
            Text.assemble(
                "formatted string ",
                (self.raw_formatted_string, "config"),
                " resulted in empty string from using the following tags:",
            )
        )
        for tag_name in Taggable.get_tag_names():
            message.append(
                Text.assemble((tag_name, "tag"), f" {getattr(self.taggable, tag_name)}")
            )
        message.append(
            Text.assemble(
                "Try using the 'required' marker (",
                ("{*{tag}}", "config"),
                ") to prevent this.",
            )
        )
        return message


class UnknownTagException(TidysicException):
    def __init__(self, tag_name: str):
        self.tag_name = tag_name

    def get_error_message(self) -> Message:
        return Text.assemble("Unknown tag name ", (self.tag_name, "tag"), ".")


def log_and_exit_on_exception(cls: Any) -> Any:  # noqa: C901
    class Inner:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self._instance = cls(*args, **kwargs)

        def __getattribute__(self, name: str) -> Any:
            try:
                return super(Inner, self).__getattribute__(name)
            except AttributeError:
                ...

            attribute = self._instance.__getattribute__(name)
            if isinstance(attribute, type(self.__init__)):  # type: ignore
                return Inner.with_logged_error(attribute)

        @staticmethod
        def with_logged_error(func: Callable[..., Any]) -> Callable[..., Any]:
            def logged_error_wrapper(*args: Any, **kwargs: Any) -> Any:
                try:
                    return func(*args, **kwargs)
                except TidysicException as e:
                    log.error(e.get_error_message())
                    exit(1)
                except Exception as e:
                    log.error(str(e))
                    exit(1)

            return logged_error_wrapper

    return Inner
