import asyncio

import click

from tekst.config import get_config
from tekst.db import init_odm, migrations
from tekst.openapi import generate_openapi_json
from tekst.platform import bootstrap as app_bootstrap
from tekst.platform import cleanup_task
from tekst.resources import call_resource_precompute_hooks
from tekst.search import create_indices_task


"""
Command line interface to some utilities of Tekst-API
"""


async def _prepare_odm() -> None:
    await init_odm()


async def _create_indices() -> None:
    await _prepare_odm()
    await create_indices_task()


async def _refresh_precomputed_cache() -> None:
    await _prepare_odm()
    await call_resource_precompute_hooks()


async def _cleanup() -> None:
    await _prepare_odm()
    await cleanup_task()


async def _maintenance() -> None:
    await _prepare_odm()
    await create_indices_task()
    await call_resource_precompute_hooks()
    await cleanup_task()


@click.command()
def bootstrap():
    """Runs the Tekst initial bootstrap procedure"""
    asyncio.run(app_bootstrap())


@click.command()
def index():
    """(Re)creates search indices"""
    asyncio.run(_create_indices())


@click.command()
def precompute():
    """Refreshes data that has to be precomputed and cached for performance"""
    asyncio.run(_refresh_precomputed_cache())


@click.command()
def cleanup():
    """Runs the internal cleanup routine for deleting outdated data"""
    asyncio.run(_cleanup())


@click.command()
def maintenance():
    """
    Runs all maintenance tasks: Indexing, data precomputation, internal cleanup
    """
    asyncio.run(_maintenance())


@click.command()
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Answer safety prompts with yes automatically",
)
def migrate(yes: bool):
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
def schema(
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
        click.echo(
            f"Saved Tekst "
            f"({'DEVELOPMENT' if get_config().dev_mode else 'PRODUCTION'} mode)"
            f" OpenAPI schema to {output_file}."
        )
    if not to_file:
        click.echo(schema_str)


@click.group()
def cli():
    """Command line interface to the main functionalities of Tekst server"""
    pass


# add individual commands to CLI app
cli.add_command(bootstrap)
cli.add_command(index)
cli.add_command(precompute)
cli.add_command(cleanup)
cli.add_command(maintenance)
cli.add_command(migrate)
cli.add_command(schema)


if __name__ == "__main__":
    cli()
