from dataclasses import dataclass
from pathlib import Path

from tidysic.exceptions import UnknownTagException
from tidysic.file.taggable import Taggable
from tidysic.logger import Logger, Text
from tidysic.settings.formatted_string import FormattedString

log = Logger()


@dataclass
class StructureStep:
    """
    Class describing a step in the tidying order. That is to say, a level of directories
    in the target folder.

    Each step is defined by the tag deciding the splitting into subfolders, and the
    template by which each subfolder will be named.
    """
    tag: str
    formatted_string: FormattedString

    def __init__(self, tag: str, formatted_string: FormattedString):
        if tag not in Taggable.get_tag_names():
            raise UnknownTagException(tag)

        self.tag = tag
        self.formatted_string = formatted_string


@dataclass
class Structure:
    """
    Class defining the target structure of tidying.

    It is composed of a list of steps, and the template by which each file will be
    named.
    """
    folders: list[StructureStep]
    track_format: FormattedString

    @classmethod
    def get_default(cls) -> "Structure":
        """
        Returns the default structure that is used unless specified otherwise.

        This structure sorts by artist, then by album.

        Returns:
            Structure: The default structure.
        """
        return cls(
            folders=[
                StructureStep("artist", FormattedString("{{artist}}")),
                StructureStep("album", FormattedString("{({date}) }{{album}}")),
            ],
            track_format=FormattedString("{{tracknumber:02d}. }{{title}}"),
        )

    @classmethod
    def parse(cls, settings_str: str) -> "Structure":
        """
        Parses a Structure from a configuration string.

        Returns:
            Structure: The structure specified in the given string.
        """
        lines = settings_str.splitlines()
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != "" and line[0] != "#"]

        if len(lines) == 0:
            raise ValueError("could not parse settings: nothing to parse")
        try:
            folders: list[StructureStep] = []
            for line in lines[:-1]:
                log.info(Text.assemble("Parsing config line ", (line, "config"), "."))
                components = line.split(" ", maxsplit=1)
                if len(components) == 1:
                    raise ValueError("expected tag name followed by format")

                [tag, raw_format] = components

                formatted_string = FormattedString(raw_format)
                folders.append(StructureStep(tag, formatted_string))

            track_line = lines[-1]
            log.info(Text.assemble("Parsing config line ", (track_line, "config"), "."))
            track_format = FormattedString(track_line)

            return cls(folders=folders, track_format=track_format)

        except ValueError as error:
            raise ValueError(f"could not parse settings: {error}.") from error

    @classmethod
    def build(cls, settings_path: Path) -> "Structure":
        """
        Parses the given configuration file, and returns the structure it defines. If no
        file is found, returns the default configuration.

        Returns:
            Structure: The structure specified in the given file, or the default
                configuration if the file does not exist.
        """
        try:
            settings = cls._load_settings(settings_path)
            return cls.parse(settings)
        except FileNotFoundError:
            return cls.get_default()

    @staticmethod
    def _load_settings(settings_path: Path) -> str:
        with open(settings_path, "r") as settings:
            return settings.read()
