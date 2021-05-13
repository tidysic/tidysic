import click
import pkg_resources

from tidysic.tidysic import Tidysic


@click.command()
@click.version_option(version=pkg_resources.require('tidysic')[0].version)
@click.option(
    '-v',
    '--verbose',
    is_flag=True,
    help='Show more information when running.'
)
@click.argument(
    'source',
    type=click.Path(exists=True, file_okay=False)
)
@click.argument(
    'target',
    type=click.Path(exists=False, file_okay=False)
)
@click.argument(
    'pattern',
    type=str
)
def run(verbose: bool, source: str, target: str, pattern: str) -> None:
    tidysic = Tidysic(source, target, pattern)
    tidysic.run()

if __name__ == '__main__':
    run()
