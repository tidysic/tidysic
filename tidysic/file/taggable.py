from dataclasses import asdict, dataclass, fields


@dataclass
class Taggable:

    album: str = 'Unknown'
    artist: str = 'Unknown'
    title: str = 'Unknown'
    genre: str = 'Unknown'
    tracknumber: str = 'Unknown'
    date: str = 'Unknown'

    @staticmethod
    def intersection(taggable: 'Taggable', other: 'Taggable') -> 'Taggable':
        """
        Return the intersection of two `Taggable`. Each field will take either
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

    def copy_tags_from(self, taggable: 'Taggable') -> None:
        self.set_tags(asdict(taggable))

    def set_tags(self, tags: dict[str, str]):
        for k, v in tags.items():
            setattr(self, k, v)
