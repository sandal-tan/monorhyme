"""A monoryhme session."""

import os
from dataclasses import dataclass, field
import typing as T
import subprocess
import sys
from pprint import pformat

from logzero import logger

from .project import PoetryProject
from .exception import CLIError


def in_git(here: str = os.path.join(os.path.abspath("."), ".")) -> T.Union[str, bool]:
    """Check to see if we are in a git project or not.
    Returns:
        The root directory of the git project, or False if not root was found
    """

    while (here := os.path.dirname(here)) != "/":
        git_path = os.path.join(here, ".git")
        if os.path.exists(git_path) and os.path.isdir(git_path):
            return here

    return False


@dataclass
class Session:
    """A CLI session for Monorhyme.

    Attributes:
        projects: The projects to manage

    """

    projects: T.List[PoetryProject] = field(default_factory=list)

    def __post_init__(self):
        root_dir = in_git()
        if root_dir:
            for dir_name, _, files in os.walk(root_dir, topdown=False):
                if "pyproject.toml" in files:
                    logger.debug("Found: %s/pyproject.toml", dir_name)
                    self.projects.append(PoetryProject(dir_name))
        else:
            raise CLIError("mr must be ran in a git repository")

    def get_latest_version(self, dependency: str) -> str:
        """Get the latest version, given a dependency.

        Args:
            dependency: The dependency for which the latest version is retrieved.

        Returns:
            The latest version

        """
        latest_version = str(
            subprocess.run(
                [sys.executable, "-m", "pip", "install", f"{dependency}==dne"],
                capture_output=True,
                text=True,
            )
        )
        latest_version = latest_version[latest_version.find("(from versions:") + 15 :]
        latest_version = latest_version[: latest_version.find(")")]
        latest_version = latest_version.replace(" ", "").split(",")[-1]
        return latest_version

    def set_version(
        self, dependency: str, version: str
    ) -> T.List[T.Tuple[str, str, str]]:
        """Set the version for a y for all packages.

        Args:
            dependency: The dependency which is set to ``version``
            version: The version constraint applied to ``dependency``

        """
        packages = []
        for _p in self.projects:
            if old_version := _p.set_version(dependency=dependency, version=version):
                logger.debug(pformat(_p._dependencies))
                packages.append((_p.project_path, old_version, version))

        return packages

    def project_has(self, dependency: str) -> bool:
        """Check whether any project requires a dependency.

        Args:
            dependency: The package that is checked to see if it is a dependency

        Returns:
            Whether or not ``dependency`` is actually a dependency

        """
        return any(_p.get_package(dependency) for _p in self.projects)

    def write(self):
        """Writes all project files."""
        for _p in self.projects:
            _p.write()
