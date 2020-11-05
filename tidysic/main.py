import os

from .argparser import create_parser
from .logger import log
from .algorithms import organise
from .os_utils import lint_folders


def run():
    parser = create_parser()
    args = parser.parse_args()

    if args.version:
        log("v0.01", prefix="Version")
        exit()
    elif args.command == 'organize':
        if args.verbose:
            log(
                f"Beginning organizing {args.source} into {args.target}",
                prefix="verbose",
                color="green"
            )
        organise(
            args.source,
            args.target,
            args.with_album,
            args.guess,
            args.dry_run
        )
    elif args.command == 'lint':
        folders = lint_folders()
        os.system(f'flake8 {folders[0]} {folders[1]}')
    elif args.command == 'lintfix':
        folders = lint_folders()
        os.system(
            f'autopep8 --in-place --recursive {folders[0]} {folders[1]}')
    else:
        parser.print_usage()


if __name__ == "__main__":
    run()