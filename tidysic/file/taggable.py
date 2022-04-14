from dataclasses import asdict, dataclass, fields
from typing import Optional


@dataclass
class Taggable:

    album: Optional[str] = None
    artist: Optional[str] = None
    title: Optional[str] = None
    genre: Optional[str] = None
    tracknumber: Optional[str] = None
    date: Optional[str] = None

    def copy_tags_from(self, taggable: "Taggable") -> None:
        self.set_tags(asdict(taggable))

    def set_tags(self, tags: dict[str, str]) -> None:
        for k, v in tags.items():
            setattr(self, k, v)

    @staticmethod
    def intersection(taggables: tuple["Taggable", ...]) -> Optional["Taggable"]:
        """
        Returns the intersection of any number of `Taggables`. Each field will either
        take the common value, or stay `None`.

        Args:
            taggables (tuple[Taggable]): Collection of taggables of which the
                intersection will be computed.

        Returns:
            Taggable: `Taggable` whose each tag is either the same as all of the given
                `Taggables`, or None.
        """
        if len(taggables) == 0:
            return None
        reference = taggables[0]
        if len(taggables) < 2:
            return reference

        taggables_intersection = Taggable()

        for field in fields(reference):
            reference_value = getattr(reference, field.name)
            if all(
                getattr(taggable, field.name) == reference_value
                for taggable in taggables[1:]
            ):
                setattr(taggables_intersection, field.name, reference_value)

        return taggables_intersection

    @staticmethod
    def get_tag_names() -> tuple[str, ...]:
        return tuple(field.name for field in fields(Taggable))

    @staticmethod
    def get_numeric_tag_names() -> tuple[str, ...]:
        return ("date", "tracknumber")

    @staticmethod
    def get_non_numeric_tag_names() -> tuple[str, ...]:
        return ("album", "artist", "title", "genre")
