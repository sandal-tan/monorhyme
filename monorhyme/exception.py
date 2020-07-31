"""Monorhyme Exceptions."""

import sys

import click
from .color import Foreground


class CLIError(Exception):
    """"An error that is rendered on the CLI."""

    def __init__(self, msg: str):
        click.echo(Foreground.red(msg))
        sys.exit(1)
