from typing import NamedTuple

from tidysic.tag import Tag
from tidysic.formatted_string import FormattedString


class OrderingStep(NamedTuple):

    tag: Tag
    format: FormattedString


class Ordering:

    def __init__(self, steps: list[OrderingStep] = []):
        self.steps = steps

    def is_terminal(self) -> bool:
        '''
        Convenience method used for knowing if we reached the last step of the
        ordering.

        Returns:
            bool: True if the ordering consists of a single step.
        '''
        return len(self.steps) == 1

    def sub_ordering(self):
        '''
        Convenience method used to get the ordering consisting of all the steps
        below the first one.

        Returns:
            Ordering: Ordering consisting of all of self's steps except for the
                first one.
        '''
        if self.is_terminal():
            raise Exception("Ordering reached its end")
        return Ordering(self.steps[1:])
