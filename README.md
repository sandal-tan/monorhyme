# Monorhyme - Standardize version constraints across many Poetry projects.

While this tool will work for single project repos, it will not provide much use over `poetry` itself. `mr` (Monorhyme)
shines in mono-repos.

## Usage

```shell
# List all defined ependencies of all projects in the git repo
% mr ls
bandit
black
click
logzero
mypy
pylint
pytest
python
tomlkit

# List all occurances of logzero
% mr ls pytest
| project                       | development | version | git  | branch | rev  | tag  | path | url  | python | markers | allow_prereleases | extras | optional |
|-------------------------------|-------------|---------|------|--------|------|------|------|------|--------|---------|-------------------|--------|----------|
| /.../monorhyme/pyproject.toml | True        | ^5.2    | None | None   | None | None | None | None | None   | None    | False             | []     | False    |

# Set all projects pytest version contraint to the latest value
% mr set pytest latest
Using 6.0.1 for pytest
/.../monorhyme/pyproject.toml (^5.2 -> ^6.0.1)

# Set all entries of click to ^7.0.1
% mr set click 7.0.1
/.../monorhyme/pyproject.toml (^7.1.2 -> 7.0.1)
```

## Why

I use `mr` to get all of my depenecies pinned to the most recent possible versions:
```shell
# Update everything to latest
% for dep in $(mr ls); do
      mr set $dep latest
  done

# Lock all of the projects. If this step fails, I use `mr set` to set the pins for items taht are causing the lock 
# to fail. Once all version constraints are solved, this will succeed
% find . -type f -name 'pyproject.toml' -execdir poetry lock \;

% Install all of the projects
% find . -type f -name 'pyproject.toml' -execdir poetry install \;
```

`lock` and `install` are in two separate calls bcause when I tried `update`, things were installing strangely.


## To Do

- White-list certain version deviations
- Support other sections of `pyproject.toml` like black
