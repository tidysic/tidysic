from sys import exit
from pathlib import Path
from typing import Any, Optional

import click
import pkg_resources

from tidysic.exceptions import TidysicException
from tidysic.logger import LogLevel, error, set_log_level
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
    type=Path(exists=True, file_okay=True),
    help="Optional, path to a .tidysic config file.",
)    
@click.argument("source", type=Path(exists=True, file_okay=False))
@click.argument("target", type=Path(exists=False, file_okay=False))
def run(verbose: bool, config_path: Optional[Path], source: Path, target: Path) -> None:
    if verbose:
        set_log_level(LogLevel.INFO)
    try:
        tidysic = Tidysic(source, target, config_path)
        tidysic.run()
    except TidysicException as e:
        error(e.get_error_message())
        exit(1)
    except Exception as e:
        pass
        error(str(e))
        exit(1)


if __name__ == "__main__":
    run()
