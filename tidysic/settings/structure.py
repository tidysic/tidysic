from dataclasses import dataclass

from tidysic.exceptions import UnknownTagException
from tidysic.file.taggable import Taggable
from tidysic.logger import Text, info
from tidysic.settings.formatted_string import FormattedString


@dataclass
class StructureStep:
    tag: str
    formatted_string: FormattedString

    def __init__(self, tag: str, formatted_string: FormattedString):
        if tag not in Taggable.get_tag_names():
            raise UnknownTagException(tag)

        self.tag = tag
        self.formatted_string = formatted_string


@dataclass
class Structure:
    folders: list[StructureStep]
    track_format: FormattedString

    @classmethod
    def get_default(cls) -> "Structure":
        return cls(
            folders=[
                StructureStep("artist", FormattedString("{{artist}}")),
                StructureStep("album", FormattedString("{({date}) }{{album}}")),
            ],
            track_format=FormattedString("{{tracknumber:02d}. }{{title}}"),
        )

    @classmethod
    def parse(cls, settings_str: str) -> "Structure":
        lines = settings_str.splitlines()
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line != "" and line[0] != "#"]

        if len(lines) == 0:
            raise ValueError("could not parse settings: nothing to parse")
        try:
            folders: list[StructureStep] = []
            for line in lines[:-1]:
                info(Text.assemble("Parsing config line ", (line, "config"), "."))
                components = line.split(" ", maxsplit=1)
                if len(components) == 1:
                    raise ValueError("expected tag name followed by format")

                [tag, raw_format] = components

                formatted_string = FormattedString(raw_format)
                folders.append(StructureStep(tag, formatted_string))

            track_line = lines[-1]
            info(Text.assemble("Parsing config line ", (track_line, "config"), "."))
            track_format = FormattedString(track_line)

            return cls(folders=folders, track_format=track_format)

        except ValueError as error:
            raise ValueError(f"could not parse settings: {error}.") from error
