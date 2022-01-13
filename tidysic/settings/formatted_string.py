import re
from abc import ABC, abstractmethod

from tidysic.exceptions import EmptyStringException
from tidysic.file.taggable import Taggable
from tidysic.logger import Logger

log = Logger()


class _Unit(ABC):
    @abstractmethod
    def write(self, taggable: Taggable) -> str:
        pass

    @classmethod
    def create(cls, raw_string: str) -> "_Unit":
        try:
            return _SubstitutableUnit(raw_string)
        except ValueError as e:
            log.warn([str(e), "Ignoring and treating as constant."])
        except Exception:
            pass
        return _TrivialUnit(raw_string)


class _SubstitutableUnit(_Unit):
    def __init__(self, raw_string: str):
        pattern = r"(\*?)(.*)\{(\w*)(\:.+)?\}(.*)"
        match = re.fullmatch(pattern, raw_string)

        if match is None:
            raise Exception()

        self.is_required = match.group(1) == "*"
        self.text_before = match.group(2)
        self.tag_name = match.group(3)
        self.format_spec = match.group(4)
        self.text_after = match.group(5)

        if self.tag_name not in Taggable.get_tag_names():
            raise ValueError(f"unknown tag name [yellow]{self.tag_name}[/yellow].")

    def write(self, taggable: Taggable) -> str:
        value = self.get_value(taggable)
        if value == "":
            if self.is_required:
                return f"Unknown {self.tag_name}"
            else:
                return ""

        return "".join((self.text_before, value, self.text_after))

    def get_value(self, taggable: Taggable) -> str:
        value = getattr(taggable, self.tag_name, None)
        if value is None:
            return ""
        else:
            if self.tag_name in Taggable.get_numeric_tag_names():
                if self.tag_name == "tracknumber":
                    match = re.fullmatch(r"(\d+)/\d+", value)
                    if match is not None:
                        value = match.group(1)
                value = int(value)
            if self.format_spec is not None:
                value = f"{{{self.format_spec}}}".format(value)
            return str(value)


class _TrivialUnit(_Unit):
    def __init__(self, string: str):
        self.string = string

    def write(self, taggable: Taggable) -> str:
        return self.string


class FormattedString:
    def __init__(self, raw_string: str):
        self._raw_string = raw_string
        self._units: list[_Unit] = []
        self._build_units()

    def _build_units(self) -> None:
        # Substitutable units are found by looking for exactly two sets of curly
        # brackets.
        pattern = r"\{(.*?\{.*?\}.*?)\}"
        split = re.split(pattern, self._raw_string)

        while split:
            self._units.append(_Unit.create(split.pop(0)))

    def write(self, taggable: Taggable) -> str:
        """
        Produces the string built using the tags found in the given taggable.
        """
        return_string = "".join(unit.write(taggable) for unit in self._units)

        if len(return_string) == 0:
            raise EmptyStringException(self._raw_string, taggable)

        return return_string
