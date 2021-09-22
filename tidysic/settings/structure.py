from dataclasses import dataclass

from tidysic.file.taggable import Taggable
from tidysic.settings.formatted_string import FormattedString


@dataclass
class StructureStep:
    tag: str
    formatted_string: FormattedString

    def __init__(self, tag: str, formatted_string: FormattedString):
        if tag not in Taggable.get_tag_names():
            raise ValueError(f"unknown tag name '{tag}'")

        self.tag = tag
        self.formatted_string = formatted_string


@dataclass
class Structure:
    folders: list[StructureStep]
    track_format: FormattedString


default_structure = Structure(
    folders=[
        StructureStep("artist", FormattedString("{{artist}}")),
        StructureStep("album", FormattedString("{({date}) }{{album}}")),
    ],
    track_format=FormattedString("{{tracknumber}. }{{title}}"),
)
