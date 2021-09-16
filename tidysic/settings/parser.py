from tidysic.settings.formatted_string import FormattedString
from tidysic.settings.structure import Structure, StructureStep


def parse_settings(settings_file: str) -> Structure:
    structure: Structure = []

    with open(settings_file, "r") as file:
        try:
            for i, line in enumerate(file):
                line = line.strip()
                if line[0] == "#":
                    continue

                [tag, raw_format] = line.split(" ", maxsplit=1)
                formatted_string = FormattedString(raw_format)
                structure.append(StructureStep(tag, formatted_string))

        except ValueError as error:
            raise ValueError(f"Could not parse settings file: {error}")

    return structure
