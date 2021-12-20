import pytest
from tidysic.settings.structure import Structure

settings_ok = """\
artist {{artist}}
{{tracknumber:02d}. }{{title}}
"""

settings_invalid_tag = """\
invalid_tag {{artist}}
{{title}}
"""

settings_invalid_format = """\
artist {{artist}}
{title}
"""

settings_tag_in_step = """\
artist {{artist}}
{{album}}
{{title}}
"""


def test_parser():
    Structure.parse(settings_ok)

    with pytest.raises(ValueError):
        Structure.parse(settings_invalid_tag)
    with pytest.raises(ValueError):
        Structure.parse(settings_invalid_format)
    with pytest.raises(ValueError):
        Structure.parse(settings_tag_in_step)
