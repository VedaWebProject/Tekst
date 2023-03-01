import asyncio

import click

from textrig.config import TextRigConfig, get_config


"""
Command line interface to the main functionalities of TextRig server
"""


_cfg: TextRigConfig = get_config()


async def _get_and_write_openapi_schema(
    to_file: bool, output_file: str, indent: int, sort_keys: bool, quiet: bool
):
    import json

    from asgi_lifespan import LifespanManager
    from httpx import AsyncClient

    from textrig.app import app

    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://test") as client:
            resp = await client.get(f"{_cfg.doc.openapi_url}")
            if not resp.status_code == 200:
                click.echo(
                    "Error: Request to TextRig server "
                    f"failed with code {resp.status_code}",
                    err=True,
                )
            else:
                schema = resp.json()
                json_dump_args = {
                    "skipkeys": True,
                    "indent": indent or None,
                    "sort_keys": sort_keys,
                }
                if to_file:
                    with open(output_file, "w") as f:
                        json.dump(schema, f, **json_dump_args)
                    if not quiet:
                        click.echo(
                            f"Saved TextRig "
                            f"({'development' if _cfg.dev_mode else 'production'} mode)"
                            f" OpenAPI schema to {output_file}."
                        )
                else:
                    click.echo(json.dumps(schema, **json_dump_args))


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
    Exports TextRig's OpenAPI schema to a JSON file
    (Important: The active TextRig environment variables might influence the schema!)
    """
    asyncio.run(
        _get_and_write_openapi_schema(
            to_file=to_file,
            output_file=output_file,
            indent=indent,
            sort_keys=sort_keys,
            quiet=quiet,
        )
    )


@click.command()
@click.option(
    "--host",
    "-h",
    default=_cfg.uvicorn_host,
    help="Server host (dynamic default from environment)",
    show_default=True,
)
@click.option(
    "--port",
    "-p",
    default=_cfg.uvicorn_port,
    help="Server port (dynamic default from environment)",
    show_default=True,
)
@click.option(
    "--reload",
    "-r",
    is_flag=True,
    help="Hot-reload on source changes (only if TEXTRIG_DEV_MODE env var is true)",
    show_default=True,
)
def run(host: str, port: int, reload: bool):
    """Runs TextRig server via Uvicorn ASGI"""

    _cfg.uvicorn_host = host
    _cfg.uvicorn_port = port

    import uvicorn

    uvicorn.run(
        "textrig.app:app",
        host=_cfg.uvicorn_host,
        port=_cfg.uvicorn_port,
        reload=_cfg.dev_mode and reload,
        log_config=None,
    )


@click.group()
def cli():
    """Command line interface to the main functionalities of TextRig server"""
    pass


# add individual commands to CLI app
cli.add_command(schema)
cli.add_command(run)


if __name__ == "__main__":
    cli()
