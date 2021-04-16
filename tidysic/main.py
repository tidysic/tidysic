from tidysic.argparser import create_parser
from tidysic.tidysic import Tidysic

from tidysic.ordering import Ordering, OrderingStep
from tidysic.tag import Tag
from tidysic.formatted_string import FormattedString


def run():
    parser = create_parser()
    args = parser.parse_args()

    tidysic = Tidysic(args)
    if not args["with_album"]:
        tidysic.ordering = Ordering(
            OrderingStep(Tag.Artist, FormattedString("{{artist}}")),
            OrderingStep(Tag.Title, FormattedString("{{track}. }{{title}}"))
        )

    tidysic.organize()


if __name__ == '__main__':

    run()
