from .argparser import create_parser
from .logger import log
from .algorithms import organize


def run():
    parser = create_parser()
    args = parser.parse_args()

    print("SALUT")

    if args.version:
        log('v0.01', prefix='Version')
        exit()

    if args.verbose:
        log(
            f'Beginning organizing {args.source} into {args.target}',
            prefix='verbose',
            color='green'
        )
    organize(
        args.source,
        args.target,
        args.with_album,
        args.guess,
        args.dry_run,
        args.verbose
    )


if __name__ == '__main__':

    run()
