import asyncio
import os
import shutil

from pathlib import Path
from typing import get_args

import click

from beanie import PydanticObjectId
from beanie.operators import Eq, In

from tekst.config import get_config
from tekst.errors import TekstHTTPException
from tekst.models.resource import (
    ResourceBaseDocument,
    ResourceExportFormat,
    res_exp_fmt_info,
)
from tekst.openapi import generate_openapi_json


"""
Command line interface to some utilities of Tekst-API
"""


async def _create_indices() -> None:
    from tekst import db, search

    await db.init_odm()
    await search.create_indices_task()
    await search.close()
    await db.close()


async def _refresh_precomputed_cache(force: bool) -> None:
    from tekst import db, resources

    await db.init_odm()
    await resources.call_resource_precompute_hooks(force=force)
    await db.close()


async def _cleanup() -> None:
    from tekst import db, platform

    await db.init_odm()
    await platform.cleanup_task()
    await db.close()


async def _maintenance() -> None:
    from tekst import db, platform, resources, search

    await db.init_odm()
    await search.create_indices_task()
    await resources.call_resource_precompute_hooks()
    await platform.cleanup_task()
    await search.close()
    await db.close()


async def _export(
    resource_ids: list[PydanticObjectId] | None,
    *,
    formats: list[ResourceExportFormat],
    output_dir_path: Path,
    quiet: bool = False,
    delete: bool = False,
) -> None:
    # check output path
    if not output_dir_path.exists():
        output_dir_path.mkdir(parents=True)
    if not output_dir_path.is_dir():
        click.echo(f"Output directory {output_dir_path} is not a directory", err=True)
        exit(1)

    # prepare system
    from tekst import db, resources
    from tekst.routers import resources as resources_router

    await db.init_odm()

    # delete all existing files in output directory
    if delete:
        if not quiet:
            click.echo(f"Deleting all existing files in {output_dir_path} ...")
        for child in output_dir_path.iterdir():
            if child.is_file():
                child.unlink()

    # call precompute hooks
    await resources.call_resource_precompute_hooks()

    # get IDs of resources to export
    target_resources = await ResourceBaseDocument.find(
        Eq(ResourceBaseDocument.public, True),
        In(ResourceBaseDocument.id, resource_ids) if resource_ids else {},
        with_children=True,
    ).to_list()

    # give feedback on resources that could not be found
    for res in resource_ids or []:
        if res not in [res.id for res in target_resources]:
            click.echo(f"Resource ID {res} not found or not public", err=True)

    # run exports
    if not target_resources:
        click.echo("No resources to export", err=True)
        exit(1)
    cfg = get_config()
    for res in target_resources:
        res_id_str = str(res.id)
        for fmt in formats:
            if not quiet:
                click.echo(f"Exporting resource {res_id_str} as {fmt} ...")
            try:
                export_props = await resources_router.export_resource_contents_task(
                    user=None,
                    cfg=cfg,
                    resource_id=res.id,
                    export_format=fmt,
                )
            except TekstHTTPException as e:
                if e.detail.detail.key == "unsupportedExportFormat":
                    click.echo(
                        f"Resource {res_id_str} does not support export format {fmt}",
                        err=True,
                    )
                    continue
                else:
                    raise

            # move exported file to output directory
            source_path = cfg.temp_files_dir / export_props["artifact"]
            target_ext = res_exp_fmt_info[fmt]["extension"]
            target_path = output_dir_path / f"{res_id_str}_{fmt}.{target_ext}"
            shutil.copy(source_path, target_path)
            os.remove(source_path)
            if not quiet:
                click.echo(f"Exported resource {res_id_str} as {str(target_path)}.")

    await db.close()


@click.command()
def bootstrap():
    """Runs the Tekst initial bootstrap procedure"""
    from tekst import platform

    asyncio.run(platform.bootstrap())


@click.command()
def index():
    """(Re)creates search indices"""
    asyncio.run(_create_indices())


@click.command()
@click.option(
    "--force",
    "-f",
    is_flag=True,
    help="Force regeneration of precomputed data even if system thinks it's up-to-date",
)
def precompute(force: bool):
    """Refreshes data that has to be precomputed and cached for performance"""
    asyncio.run(_refresh_precomputed_cache(force=force))


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
    "--output",
    "-o",
    required=False,
    default="/tmp/tekst_resource_export/",
    show_default=True,
    help="Output directory to write to",
)
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    default=False,
    help="Don't output anything (except errors and warnings)",
)
@click.option(
    "--delete",
    "-d",
    is_flag=True,
    default=False,
    help="Delete all existing files in the output directory",
)
def export(
    resource: list[str] | None,
    format: list[ResourceExportFormat],
    output: str,
    quiet: bool = False,
    delete: bool = False,
) -> None:
    """
    Exports the contents of the given resources (or all)
    using the given formats (or all) to the given output directory
    """
    asyncio.run(
        _export(
            [PydanticObjectId(res_id) for res_id in resource] if resource else None,
            formats=format,
            output_dir_path=Path(output),
            quiet=quiet,
            delete=delete,
        )
    )


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
cli.add_command(export)


if __name__ == "__main__":
    cli()
