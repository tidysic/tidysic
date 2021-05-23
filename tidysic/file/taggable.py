from dataclasses import dataclass, asdict, fields

from typing import Optional


@dataclass
class Taggable:

    album: Optional[str] = None
    artist: Optional[str] = None
    title: Optional[str] = None
    genre: Optional[str] = None
    tracknumber: Optional[str] = None
    date: Optional[str] = None

    def copy_tags_from(self, taggable: 'Taggable'):
        self.set_tags(asdict(taggable))

    def set_tags(self, tags: dict[str, str]):
        for k, v in tags.items():
            setattr(self, k, v)

    @staticmethod
    def intersection(taggable: 'Taggable', other: 'Taggable') -> 'Taggable':
        """
        Returns the intersection of two `Taggable`. Each field will take either
        the common value, or keep its default value ("Unknown").
        """
        taggables_intersection = Taggable()

        for field in fields(taggable):
            attr = getattr(taggable, field.name)
            other_attr = getattr(other, field.name)
            if attr == other_attr:
                value = attr
                setattr(taggables_intersection, field.name, value)

        return taggables_intersection

    @staticmethod
    def get_tag_names() -> tuple[str, ...]:
        return tuple(
            field.name
            for field in fields(Taggable)
        )
