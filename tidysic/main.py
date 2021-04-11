from tidysic.argparser import create_parser
from tidysic.tidysic import organize


def run():
    parser = create_parser()
    args = parser.parse_args()

    organize(
        args.source,
        args.target,
        args.with_album,
        args.with_clutter,
        args.guess,
        args.dry_run,
        args.verbose
    )


if __name__ == '__main__':

    run()
