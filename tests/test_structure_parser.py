import pytest
from tidysic.settings.parser import parse_settings

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
    parse_settings(settings_ok)

    with pytest.raises(ValueError):
        parse_settings(settings_invalid_tag)
    with pytest.raises(ValueError):
        parse_settings(settings_invalid_format)
    with pytest.raises(ValueError):
        parse_settings(settings_tag_in_step)
