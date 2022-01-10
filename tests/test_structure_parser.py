import pytest
from tidysic.settings.structure import Structure

settings_ok = """\
artist {{artist}}
{{tracknumber:02d}. }{{title}}
"""

settings_tag_in_step = """\
artist {{artist}}
{{album}}
{{title}}
"""


def test_parser():
    Structure.parse(settings_ok)

    with pytest.raises(ValueError):
        Structure.parse(settings_tag_in_step)
