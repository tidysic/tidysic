import click
import pkg_resources

from tidysic.formatted_string import FormattedString
from tidysic.ordering import Ordering, OrderingStep
from tidysic.tag import Tag
from tidysic.tidysic import Tidysic


@click.command()
@click.version_option(version=pkg_resources.require('tidysic')[0].version)
@click.option(
    '-v',
    '--verbose',
    is_flag=True,
    help='Show more information when running.'
)
@click.option(
    '--with-album',
    is_flag=True,
    help='Create an album directory inside the artist directory.'
)
@click.option(
    '--with-clutter',
    is_flag=True,
    help='Move non-audio files along with their audio neighbor files.'
)
@click.option(
    '-i',
    '--interactive',
    is_flag=True,
    help='Will prompt user input for missing tags.'
)
@click.option(
    '-d',
    '--dry-run',
    is_flag=True,
    help=('Do nothing on the files themselves, but print out the actions that '
          'would happen.')
)
@click.argument(
    'source',
    type=click.Path(exists=True, file_okay=False),
)
@click.argument(
    'target',
    type=click.Path(exists=False, file_okay=False),
)
def run(
    verbose: bool,
    with_album: bool,
    with_clutter: bool,
    interactive: bool,
    dry_run: bool,
    source: str,
    target: str
):
    '''
    Organize music contents of the SOURCE folder inside the TARGET folder (will
    be created if needed).
    '''
    tidysic = Tidysic(
        input_dir=source,
        output_dir=target,
        dry_run=dry_run,
        interactive=interactive,
        with_clutter=with_clutter,
        verbose=verbose
    )

    if not with_album:
        tidysic.ordering = Ordering([
            OrderingStep(Tag.Artist, FormattedString('{{artist}}')),
            OrderingStep(Tag.Title, FormattedString('{{track}. }{{title}}'))
        ])

    tidysic.organize()


if __name__ == '__main__':
    run()
