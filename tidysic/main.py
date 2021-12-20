from pathlib import Path
from typing import Any, Optional

import click
import pkg_resources

from tidysic.tidysic import Tidysic


def dump_config(ctx: click.Context, param: click.Parameter, value: Any) -> None:
    if not value or ctx.resilient_parsing:
        return
    with pkg_resources.resource_stream("tidysic.settings", ".tidysic.default") as fp:
        default_config = fp.read()
        click.echo(default_config)
    ctx.exit()


@click.command()
@click.option(
    "-v", "--verbose", is_flag=True, help="Show more information when running."
)
@click.version_option(version=pkg_resources.require("tidysic")[0].version)
@click.option(
    "--dump-config",
    is_flag=True,
    callback=dump_config,
    expose_value=False,
    is_eager=True,
    help="Dump the default config and exit.",
)
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, file_okay=True),
    help="Optional, path to a .tidysic config file.",
)
@click.argument("source", type=click.Path(exists=True, file_okay=False))
@click.argument("target", type=click.Path(exists=False, file_okay=False))
def run(verbose: bool, config_path: Optional[Path], source: str, target: str) -> None:
    tidysic = Tidysic(source, target, config_path)
    tidysic.run()


if __name__ == "__main__":
    run()
