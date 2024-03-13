import asyncio

import click

from tekst.config import TekstConfig, get_config
from tekst.openapi import generate_openapi_schema
from tekst.setup import app_setup


"""
Command line interface to the main functionalities of Tekst server
"""


_cfg: TekstConfig = get_config()


@click.command()
def setup():
    asyncio.run(app_setup(_cfg))


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
    help="Don't output anything (only effective if --to-file flag is not set)",
)
def schema(to_file: bool, output_file: str, indent: int, sort_keys: bool, quiet: bool):
    """
    Exports Tekst's OpenAPI schema to a JSON file
    (Important: The active Tekst environment variables might influence the schema!)
    """
    schema = asyncio.run(
        generate_openapi_schema(
            to_file=to_file,
            output_file=output_file,
            indent=indent,
            sort_keys=sort_keys,
        )
    )
    if to_file and not quiet:
        click.echo(
            f"Saved Tekst "
            f"({'development' if _cfg.dev_mode else 'production'} mode)"
            f" OpenAPI schema to {output_file}."
        )
    if not to_file:
        click.echo(schema)


@click.command()
@click.option(
    "--host",
    "-h",
    default=_cfg.dev_host,
    help="Server host (dynamic default from environment)",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    default=_cfg.dev_port,
    help="Server port (dynamic default from environment)",
    show_default=True,
)
@click.option(
    "--reload",
    "-r",
    is_flag=True,
    help="Hot-reload on source changes (only if TEKST_DEV_MODE env var is true)",
    show_default=True,
)
def run(host: str, port: int, reload: bool):
    """Runs Tekst server via Uvicorn ASGI"""

    _cfg.dev_host = host
    _cfg.dev_port = port

    import uvicorn

    uvicorn.run(
        "tekst.app:app",
        host=_cfg.dev_host,
        port=_cfg.dev_port,
        reload=_cfg.dev_mode and reload,
        log_config=None,
    )


@click.group()
def cli():
    """Command line interface to the main functionalities of Tekst server"""
    pass


# add individual commands to CLI app
cli.add_command(setup)
cli.add_command(schema)
cli.add_command(run)


if __name__ == "__main__":
    cli()
