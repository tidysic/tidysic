from dataclasses import dataclass, asdict, fields

@dataclass
class Taggable:

    album: str = None
    artist: str = None
    title: str = None
    genre: str = None
    tracknumber: str = None
    date: str = None

    def copy_tags_from(self, taggable: 'Taggable'):
        self.set_tags(asdict(taggable))

    def set_tags(self, tags: dict[str, str]):
        for k, v in tags.items():
            setattr(self, k, v)

    @staticmethod
    def get_tag_names() -> tuple[str]:
        return tuple(
            field.name
            for field in fields(Taggable)
        )
