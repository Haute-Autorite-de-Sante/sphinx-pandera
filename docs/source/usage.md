# Usage

## Requirements

- TODO

# Installation

You can install Sphinx Pandera via [pip](https://pip.pypa.io/):

```shell script
pip install sphinx-pandera
```

# Development

> 📝 **Note**
> For convenience, many of the below processes are abstracted away
> and encapsulated in single [Make](https://www.gnu.org/software/make/) targets.

> 🔥 **Tip**
> Invoking `make` without any arguments will display
> auto-generated documentation on available commands.

## Package and Dependencies Installation

Make sure you have Python 3.9+ and [poetry](https://python-poetry.org/)
installed and configured.

To install the package and all dev dependencies, run:

```shell script
make provision-environment
```

> 🔥 **Tip**
> Invoking the above without `poetry` installed will emit a
> helpful error message letting you know how you can install poetry.

## Testing

We use [pytest](https://pytest.readthedocs.io/) for our testing framework.

To invoke the tests, run:

```shell script
make test
```

## Code Quality

We use [pre-commit](https://pre-commit.com/) for our code quality
static analysis automation and management framework.

To invoke the analyses and auto-formatting over all version-controlled files, run:

```shell script
make lint
```

> 🚨 **Danger**
> CI will fail if either testing or code quality fail,
> so it is recommended to automatically run the above locally
> prior to every commit that is pushed.

### Automate via Git Pre-Commit Hooks

To automatically run code quality validation on every commit (over to-be-committed
files), run:

```shell script
make install-pre-commit-hooks
```

> ⚠️ Warning !
> This will prevent commits if any single pre-commit hook fails
> (unless it is allowed to fail)
> or a file is modified by an auto-formatting job;
> in the latter case, you may simply repeat the commit and it should pass.

## Documentation

```shell script
make docs-clean docs-html
```

> 📝 **Note**
> This command will generate html files in `docs/_build/html`.
> The home page is the `docs/_build/html/index.html` file.

## Publishing a new release on pypi

1. Check in `pyproject.toml` that the version of the package is correct
1. `git tag -a 0.0.3` the revision you want to release
1. `git push --tags`
1. In Gitlab create a new release from tag
1. Sync repo in github
1. ` export POETRY_PYPI_TOKEN_PYPI=<your scoped pypi token>`
1. `poetry publish --build` to push to pypi
