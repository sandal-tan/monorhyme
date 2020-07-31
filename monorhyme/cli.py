"""CLI Entrypoint."""

import logging
import typing as T
import subprocess
import sys
from functools import wraps

import click
from logzero import logger
import logzero

from .session import Session
from . import table, color
from .exception import CLIError

DEFAULT_VERSION_CONSTRAINT: str = "^"
"""The default version constraint to apply."""


def fail_clean(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise CLIError(str(e))

    return _wrapper


@click.group()
@click.option("--verbose", "-v", help="Turn on verbose output", is_flag=True)
@click.pass_context
@fail_clean
def monorhyme(ctx, verbose: bool):
    """Monorhyme - manage poetry in a monorepo."""
    logzero.loglevel(logging.WARNING if not verbose else logging.DEBUG)
    ctx.obj = Session()


@monorhyme.command(name="ls")
@click.argument("package", required=False)
@click.pass_obj
def _list(session: Session, package: T.Optional[str] = None):
    """List all found veresions for a depdency."""
    if package:
        _results = [
            (project.get_package(package), project.project_path)
            for project in session.projects
        ]
        _results = [r for r in _results if r[0] is not None]
        if _results:
            _table = table.Table(
                columns=[table.Column(name="project")]
                + [table.Column(name=k) for k in _results[0][0].__dict__ if k != "name"]
            )
            for _package, path in _results:
                _table.add_row(
                    **{k: v for k, v in _package.__dict__.items() if k != "name"},
                    project=path,
                )
            click.echo(_table)
        else:
            raise CLIError(f"`{package}` not declared as a depdency")
    else:
        deps = set()
        for p in session.projects:
            deps.update(set(p._dependencies.keys()))
        click.echo("\n".join(sorted(deps)))


@monorhyme.command(name="set")
@click.argument("dependency")
@click.argument("version")
@click.pass_obj
def _set(session: Session, dependency: str, version: str) -> None:
    """Set the version for a depdency in the monorepo."""
    if not session.project_has(dependency):
        raise CLIError(f"No project requires `{dependency}`")
    if version == "latest":
        latest_version = session.get_latest_version(dependency)
        click.echo(
            f"Using {color.Foreground.cyan(latest_version)} for {color.Foreground.green(dependency)}"
        )
        version = f"{DEFAULT_VERSION_CONSTRAINT}{latest_version}"
    updated_packages = session.set_version(version=version, dependency=dependency)
    if updated_packages:
        click.echo(
            "\n".join(
                f"{color.Foreground.blue(path)} ({color.Foreground.red(old)} -> {color.Foreground.green(new)})"
                for path, old, new in updated_packages
            )
        )
        session.write()
    else:
        click.echo("All projects are already up to date.")
