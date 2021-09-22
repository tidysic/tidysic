from tidysic.file.taggable import Taggable
from tidysic.settings.formatted_string import FormattedString
from tidysic.settings.structure import Structure, StructureStep


def parse_settings(settings_str: str) -> Structure:

    lines = settings_str.splitlines()
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line != "" and line[0] != "#"]

    if len(lines) == 0:
        raise ValueError("Could not parse settings: nothing to parse")
    try:
        folders: list[StructureStep] = []
        for line in lines[:-1]:
            components = line.split(" ", maxsplit=1)
            if len(components) == 1:
                raise ValueError("expected tag name followed by format")

            [tag, raw_format] = components
            if tag not in Taggable.get_tag_names():
                raise ValueError(f"invalid tag '{tag}'")

            formatted_string = FormattedString(raw_format)
            folders.append(StructureStep(tag, formatted_string))

        track_line = lines[-1]
        track_format = FormattedString(track_line)

        return Structure(folders=folders, track_format=track_format)

    except ValueError as error:
        raise ValueError(f"Could not parse settings: {error}.") from error


default_config = """\
# This is the default configuration file for your tidy music folder.
# You will define here how the music will be sorted into a hierarchy of folders.

# Each line describes a step in the hierarchy, it must be formatted as follow:

# The first word is the tag by which to sort the files, it must be one of the
# following:
#
#     album, artist, title, genre, tracknumber, date

# The rest of the line describes how to format the folder's name. Here is how it works:
#
# The value of any tag can be inserted using double curly brackets like this:
#     {{album}}
#
# If the tag value is not set, this will be replaced by a blank.
#
# You can use the space between the sets of brackets to add text that will only
# be displayed if the value is set, for instance,
#     {{tracknumber}. }{{title}}
# will turn into, for instance,
#     1. Intro
# or
#     Intro
# depending on whether the track number is set.
#
# You can use formatting options as in python, for instance you can pad the
# track number like so:
#     {{tracknumber:02d}. }{{title}}
# to get
#     01. Intro

# After the lines describing the folders, you must describe the formatting of
# the tracks themselves, using the same rules as before.

artist {{artist}}
album {({date}) }{{album}}
{{tracknumber:02d}. }{{title}}
"""
