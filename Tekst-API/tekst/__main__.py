"""
This is the main entry point for the Tekst-API command line interface.
The actual CLI is loaded from the cli module.
"""

from tekst.cli import cli


if __name__ == "__main__":
    cli()
