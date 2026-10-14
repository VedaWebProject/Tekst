import asyncio

from pathlib import Path
from typing import get_args

import click

from beanie import PydanticObjectId

from tekst.cli import cleanup, export, index, maintenance, precompute
from tekst.config import get_config
from tekst.models.resource import ResourceExportFormat
from tekst.openapi import generate_openapi_json


@click.command()
def bootstrap_cmd():
    """Runs the Tekst initial bootstrap procedure"""
    from tekst import platform

    asyncio.run(platform.bootstrap())


@click.command()
def index_cmd():
    """(Re)creates search indices"""
    asyncio.run(index.run())


@click.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force regeneration of precomputed data even if system thinks it's up-to-date",
)
def precompute_cmd(force: bool):
    """Refreshes data that has to be precomputed and cached for performance"""
    asyncio.run(precompute.run(force=force))


@click.command()
def cleanup_cmd():
    """Runs the internal cleanup routine for deleting outdated and invalidated data"""
    asyncio.run(cleanup.run())


@click.command()
def maintenance_cmd():
    """
    Runs all maintenance tasks: Indexing, data precomputation, internal cleanup
    """
    asyncio.run(maintenance.run())


@click.command()
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Answer safety prompts with yes automatically",
)
def migrate_cmd(yes: bool):
    """Runs the database migration procedure"""
    if not yes and not click.confirm(
        (
            "You should defenitely back up your database before migrating. "
            "Are you sure you want to run database migrations now?"
        ),
        default=False,
        abort=True,
    ):
        click.echo("Aborting database migration.")
        return
    from tekst.db import migrations

    asyncio.run(migrations.migrate())


@click.command()
@click.option(
    "--to-file",
    "-f",
    is_flag=True,
    help="Output to file defined by --output-file instead of stdout",
)
@click.option(
    "--output-file",
    "-o",
    default="openapi.json",
    help="Output file path to write to if --to-file flag is set",
    show_default=True,
)
@click.option(
    "--indent",
    "-i",
    default=2,
    help="Indent output by n whitespace characters (0 for no indentation)",
    show_default=True,
)
@click.option(
    "--sort-keys",
    "-s",
    is_flag=True,
    help="Sort keys in output JSON",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Don't output anything (only effective if --to-file is also set)",
)
def schema_cmd(
    to_file: bool,
    output_file: str,
    indent: int,
    sort_keys: bool,
    quiet: bool,
):
    """
    Exports Tekst's OpenAPI schema to a JSON file

    Important: The active Tekst environment variables might influence the schema!
    """
    schema_str = asyncio.run(
        generate_openapi_json(
            to_file=to_file,
            output_file=output_file,
            indent=indent,
            sort_keys=sort_keys,
        )
    )
    if to_file and not quiet:
        dev_mode = get_config().dev_mode
        click.echo(
            f"Saved Tekst "
            f"({'DEVELOPMENT' if dev_mode else 'PRODUCTION'} mode)"
            f" OpenAPI schema to {output_file}."
        )
    if not to_file:
        click.echo(schema_str)


@click.command()
@click.option(
    "--resource",
    "-r",
    required=False,
    default=None,
    show_default=True,
    multiple=True,
    help="ID(s) of resource(s) to export, all if not set",
)
@click.option(
    "--format",
    "-f",
    required=False,
    default=get_args(ResourceExportFormat.__value__),
    show_default=True,
    multiple=True,
    help="Format(s) to export, all if not set",
)
@click.option(
    "--out-dir",
    "-o",
    required=False,
    default="/tmp/tekst_resource_export/",
    show_default=True,
    help="Output directory to write to",
)
@click.option(
    "--delete",
    "-d",
    is_flag=True,
    default=False,
    help="Delete all existing files and directories in the output directory",
)
@click.option(
    "--archive",
    "-a",
    type=int,
    required=False,
    default=None,
    show_default=True,
    help=(
        "Archive existing export data, keep old archives for n days "
        "(n<=0: keep all; ignores --delete)"
    ),
)
@click.option(
    "--structured",
    "-s",
    is_flag=True,
    default=True,
    help="Create meaningful output directory structure instead of flat output",
)
@click.option(
    "--web-safe",
    "-w",
    is_flag=True,
    default=False,
    help="Avoid non-web-safe characters in file names or path components",
)
@click.option(
    "--browsable",
    "-b",
    is_flag=True,
    default=False,
    help=(
        "Creates index.html files listing contents in output directories "
        "(recursive, enforces --web-safe)"
    ),
)
def export_cmd(
    resource: list[str] | None,
    format: list[ResourceExportFormat],
    out_dir: str,
    delete: bool = False,
    archive: int | None = None,
    structured: bool = True,
    web_safe: bool = False,
    browsable: bool = False,
) -> None:
    """
    Exports the contents of the given resources (or all)
    using the given formats (or all) to the given output directory
    """
    asyncio.run(
        export.run(
            [PydanticObjectId(res_id) for res_id in resource] if resource else None,
            formats=format,
            out_dir=Path(out_dir),
            delete=delete,
            archive=archive,
            structured=structured,
            web_safe=web_safe,
            browsable=browsable,
        )
    )


@click.group()
def cli():
    """Command line interface to the main functionalities of Tekst server"""
    pass


# add individual commands to CLI app
cli.add_command(bootstrap_cmd)
cli.add_command(index_cmd)
cli.add_command(precompute_cmd)
cli.add_command(cleanup_cmd)
cli.add_command(maintenance_cmd)
cli.add_command(migrate_cmd)
cli.add_command(schema_cmd)
cli.add_command(export_cmd)
