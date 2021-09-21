import re

from tidysic.file.taggable import Taggable


class FormattedString:
    def __init__(self, raw_string: str):
        try:
            self.validate(raw_string)
        except ValueError as e:
            raise ValueError(f"Could not create formatted string, {e}")

        self.raw_string = raw_string

    def write(self, taggable: Taggable):
        """
        Produces the string built using the tags found in the given taggable.
        """
        pattern = r"\{(.*?\{(\w+)(:.+?)?\}.*?)\}"
        matches = re.findall(pattern, self.raw_string)

        return_string = self.raw_string

        for to_substitute, tag_name, format_spec in matches:

            value = getattr(taggable, tag_name, None)
            if value and tag_name in Taggable.get_numeric_tag_names():
                value = int(value)
            if not value and tag_name in Taggable.get_non_numeric_tag_names():
                value = f"Unknown {tag_name}"

            formattable = to_substitute.replace(
                "{%s%s}" % (tag_name, format_spec), "{%s}" % format_spec
            )
            return_string = return_string.replace(
                "{%s}" % to_substitute,
                formattable.format(value) if value else "",
                1,
            )

        return return_string

    @staticmethod
    def validate(raw_string: str):
        """
        Raises a ValueError if the given string is badly formatted.
        """
        bracket_depth = 0
        current_tag_name = ""

        for i, char in enumerate(raw_string):
            if char == "{":
                bracket_depth += 1
                if bracket_depth > 2:
                    raise ValueError(f"too many opening brackets (col {i})")

            elif char == "}":
                bracket_depth -= 1
                if bracket_depth < 0:
                    raise ValueError(f"too many closing brackets (col {i})")

                if bracket_depth == 0:
                    current_tag_name = current_tag_name.split(":")[0]
                    if current_tag_name not in Taggable.get_tag_names():
                        raise ValueError(f"unknown tag name '{current_tag_name}'")
                    current_tag_name = ""

            elif bracket_depth == 2:
                current_tag_name += char
