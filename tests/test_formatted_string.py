import pytest
from tidysic.exceptions import EmptyStringException
from tidysic.file.taggable import Taggable
from tidysic.settings.formatted_string import FormattedString


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

    with pytest.raises(EmptyStringException):
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
