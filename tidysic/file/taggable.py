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
    def get_tag_names() -> tuple[str, ...]:
        return tuple(
            field.name
            for field in fields(Taggable)
        )
