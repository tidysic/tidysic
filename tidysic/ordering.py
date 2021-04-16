from tidysic.tag import Tag
from tidysic.formatted_string import FormattedString


class OrderingStep:

    def __init__(self, tag: Tag, formatted_string: FormattedString):
        self.tag = tag
        self.format = formatted_string


class Ordering:

    def __init__(self, steps: list[OrderingStep] = []):
        self.steps = steps
    
    @property
    def is_terminal(self):
        return len(self.steps) == 1

    @property
    def sub_ordering(self):
        assert not self.is_terminal, "Ordering reached its end"
        return Ordering(self.steps[1:])
