from pathlib import Path
from typing import Any, Mapping, Optional

import click
import pkg_resources

from tidysic.logger import Logger, LogLevel
from tidysic.tidysic import Tidysic

log = Logger()


def dump_config(ctx: click.Context, param: click.Parameter, value: Any) -> None:
    """
    Prints out the default config (found in `settings/.tidysic.default`) to the console
    and exits.
    """
    if not value or ctx.resilient_parsing:
        return
    with pkg_resources.resource_stream("tidysic.settings", ".tidysic.default") as fp:
        default_config = fp.read()
        click.echo(default_config)
    ctx.exit()


class FallbackArgument(click.Argument):
    """
    Specializes `click.Argument` to provide an option that disable a required parameter.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.not_required_if: str = kwargs.pop("not_required_if")
        assert self.not_required_if, "'not_required_if' parameter required"

        super().__init__(*args, **kwargs)

    def handle_parse_result(
        self, ctx: click.Context, opts: Mapping[str, Any], args: list[Any]
    ) -> tuple[Any, list[str]]:
        self_present = self.name is not None and opts[self.name] is not None
        other_present = self.not_required_if in opts

        if other_present:
            if self_present:
                raise click.UsageError(
                    f"Illegal usage: cannot specify  `{self.name}` "
                    f"if `{self.not_required_if}` is set."
                )
            else:
                self.required = False

        return super().handle_parse_result(ctx, opts, args)


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
    type=click.Path(exists=True, file_okay=True, path_type=Path),
    help="Optional, path to a .tidysic config file.",
)
@click.option(
    "--move/--copy", help="Defines which file operations to apply. Defaults to `copy`"
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Does not apply any filesystem operation, but logs what would be done.",
)
@click.option(
    "--in-place",
    is_eager=True,
    is_flag=True,
    help=(
        "Sets the target folder to be the same as the source, and uses move operations "
        "rather than copying the files. The TARGET argument must be omitted when using "
        "this option."
    ),
)
@click.argument(
    "source",
    type=click.Path(
        exists=True,
        file_okay=False,
        path_type=Path,
    ),
)
@click.argument(
    "target",
    type=click.Path(exists=False, file_okay=False, path_type=Path),
    cls=FallbackArgument,
    not_required_if="in_place",
)
def run(
    verbose: bool,
    config_path: Optional[Path],
    dry_run: bool,
    in_place: bool,
    move: bool,
    source: Path,
    target: Path,
) -> None:
    if in_place:
        target = source
        move = True

    if verbose or dry_run:
        log.level = LogLevel.INFO

    tidysic = Tidysic(source, target, move, dry_run, config_path)
    tidysic.run()


if __name__ == "__main__":
    run()
