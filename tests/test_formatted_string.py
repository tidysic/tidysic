import pytest
from tidysic.file.taggable import Taggable
from tidysic.settings.formatted_string import FormattedString


def test_validation():
    with pytest.raises(ValueError):
        too_many_brackets = "{{{artist}}"
        FormattedString(too_many_brackets)

    with pytest.raises(ValueError):
        too_few_brackets = "{artist}}"
        FormattedString(too_few_brackets)

    with pytest.raises(ValueError):
        mismatched_brackets = "{{artist}"
        FormattedString(mismatched_brackets)

    with pytest.raises(ValueError):
        invalid_tag = "{{invalid_tag}}"
        FormattedString(invalid_tag)


def test_extra_text():
    fs = FormattedString(
        "{surrounding stuff {artist} here too }always present {{album}}"
    )

    tagged_whole = Taggable(album="Album", artist="Artist")
    assert (
        fs.write(tagged_whole)
        == "surrounding stuff Artist here too always present Album"
    )

    tagged_only_album = Taggable(album="Album")
    assert fs.write(tagged_only_album) == "always present Album"

    tagged_empty = Taggable()
    assert fs.write(tagged_empty) == "always present "


def test_empty_string():
    fs = FormattedString("{{artist}}")
    tagged = Taggable()

    with pytest.raises(RuntimeError):
        fs.write(tagged)

    fs = FormattedString("{*{artist}}")
    assert fs.write(tagged) == "Unknown artist"


def test_number_formatting():
    fs = FormattedString("{{tracknumber:03d}}")
    tagged = Taggable(tracknumber="34")
    assert fs.write(tagged) == "034"


def test_rich_tracknumber():
    fs = FormattedString("{{tracknumber:02d}}")
    tagged = Taggable(tracknumber="03/12")
    assert fs.write(tagged) == "03"
