"""A Poetry Project"""

from pprint import pformat
from dataclasses import dataclass, field
import typing as T

import toml
from logzero import logger

from .exception import CLIError


@dataclass
class PoetryDependency:
    """A container for a Poetry dependency.

    Notes:
        This does not support multiple constraints

    Attributes:
        name: The name of the dependency
        development: Whether or not it's a development dependency
        version: The version contstraints for the dependency
        git: The URL for the git repo of the dependency
        branch: The branch for which the ``git`` dependency is locked to
        rev: The commit hash of the ``git`` dependency
        tag: The tag of the ``git`` dependency
        path: The path of the dependency
        url: The URL of the dependency
        python: The python version contstraints
        markers: More complex install markers
        allow_prereleases: Whether or not to allow prelease versions
        extras: The optional extras to install for ``name``
        optional: Whether or not the dependency is an optional extra

    """

    name: str
    development: bool = False
    version: T.Optional[str] = None
    git: T.Optional[str] = None
    branch: T.Optional[str] = None
    rev: T.Optional[str] = None
    tag: T.Optional[str] = None
    path: T.Optional[str] = None
    url: T.Optional[str] = None
    python: T.Optional[str] = None
    markers: T.Optional[str] = None
    allow_prereleases: bool = False
    extras: T.List[str] = field(default_factory=list)
    optional: bool = False


@dataclass
class PoetryProject:
    """A Poetry project.

    Attributes:
        project_path: The path to the pyproject.toml file

    """

    project_path: str

    def __post_init__(self):
        if not self.project_path.endswith("/pyproject.toml"):
            self.project_path += "/pyproject.toml"
        with open(self.project_path) as project_fp:
            self._raw_file = toml.load(project_fp)
        logger.debug(pformat(self._raw_file))
        self._dependencies = {}
        for name, items in self._raw_file["tool"]["poetry"]["dependencies"].items():
            if not isinstance(items, dict):
                items = {"version": items}
            items["allow_prereleases"] = items.pop("allow-prereleases", False)
            self._dependencies[name] = PoetryDependency(
                name=name, development=False, **items
            )

        for name, items in self._raw_file["tool"]["poetry"]["dev-dependencies"].items():
            if not isinstance(items, dict):
                items = {"version": items}

            items["allow_prereleases"] = items.pop("allow-prereleases", False)
            self._dependencies[name] = PoetryDependency(
                name=name, development=True, **items
            )

    def write(self):
        """Write the `pyproject.toml` file. for the project."""
        to_write = self._raw_file
        to_write["tool"]["poetry"]["dev-dependencies"] = {
            k: v.__dict__ for k, v in self._dependencies.items() if v.development
        }
        to_write["tool"]["poetry"]["dependencies"] = {
            k: v.__dict__ for k, v in self._dependencies.items() if not v.development
        }
        with open(self.project_path, "w") as project_fp:
            toml.dump(to_write, project_fp)

    def get_package(self, package: str) -> T.Optional[PoetryDependency]:
        """Get a package if it's defined in the project."""
        return self._dependencies.get(package)

    def set_version(self, dependency: str, version: str) -> bool:
        """Set the version of a dependency in a project.

        Args:
            dependency: The dependency which has it's version set.
            version: The version constraint to apply

        Returns:
            Whether or not the version was changed

        """
        if self._dependencies[dependency].version is None:
            raise CLIError(
                f"`Dependency `{dependency}` is not managed via a version constraint"
            )
        if version != self._dependencies[dependency].version:
            self._dependencies[dependency].version = version
            return True
        return False
