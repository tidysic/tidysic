import re
from abc import ABC, abstractmethod

from tidysic.file.taggable import Taggable


class _Unit(ABC):

    @abstractmethod
    def write(self, taggable: Taggable):
        pass


class _SubstitutableUnit(_Unit):

    def __init__(self, raw_string: str):
        pattern = r"(\*?)(.*)\{(\w*)(\:.+)?\}(.*)"
        match = re.fullmatch(pattern, raw_string)

        if match is None:
            raise ValueError(f"Could not parse formatted string: '{raw_string}'.")

        self.is_required = (match.group(1) == "*")
        self.text_before = match.group(2)
        self.tag_name = match.group(3)
        self.format_spec = match.group(4)
        self.text_after = match.group(5)

    def write(self, taggable: Taggable):
        value = self.get_value(taggable)
        if value is None:
            if self.is_required:
                return f"Unknown {self.tag_name}"
            else:
                return ""
        else:
            if self.format_spec is not None:
                value = f"{{{self.format_spec}}}".format(value)

            return "".join((
                self.text_before,
                value,
                self.text_after
            ))

    def get_value(self, taggable: Taggable):
        value = getattr(taggable, self.tag_name, None)
        if value and self.tag_name in Taggable.get_numeric_tag_names():
            if self.tag_name == "tracknumber":
                match = re.fullmatch(r"(\d+)/\d+", value)
                if match is not None:
                    value = match.group(1)
            value = int(value)
        return value


class _TrivialUnit(_Unit):

    def __init__(self, string: str):
        self.string = string

    def write(self, taggable: Taggable):
        return self.string


class FormattedString:

    def __init__(self, raw_string: str):
        try:
            self.validate(raw_string)
        except ValueError as e:
            raise ValueError(f"Could not create formatted string, {e}")

        self._units: list[_Unit] = []
        self._build_units(raw_string)

    def _build_units(self, raw_string: str):
        # Substitutable units are found ba looking for exactly two sets of curly
        # brackets.
        pattern = r"\{([^\{]*\{[^\{\}]*\}[^\}]*)\}"
        split = re.split(pattern, raw_string)

        self._units.append(_TrivialUnit(split.pop(0)))
        try:
            while split:
                self._units.append(_SubstitutableUnit(split.pop(0)))
                self._units.append(_TrivialUnit(split.pop(0)))
        except ValueError as e:
            raise ValueError(f"Could not create formatted string, {e}")

    def write(self, taggable: Taggable):
        """
        Produces the string built using the tags found in the given taggable.
        """
        return_string = "".join(
            unit.write(taggable)
            for unit in self._units
        )

        if len(return_string) == 0:
            raise RuntimeError(
                "formatted string resulted in empty string. "
                "Try using the 'required' marker ({*{tag}}) to prevent this."
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

        if bracket_depth != 0:
            raise ValueError("mismatched brackets")
