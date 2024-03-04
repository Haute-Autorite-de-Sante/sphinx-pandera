"""Pytest configuration module"""

# pylint: disable=redefined-outer-name

import shutil
from pathlib import Path
from typing import Dict, List, Optional
from unittest.mock import Mock

import pytest
from sphinx.application import Sphinx
from sphinx.ext.autodoc.directive import (
    DocumenterBridge,
    process_documenter_options,
)
from sphinx.util.docutils import LoggingReporter

# sphinx fixtures for testing, most notably make_app
pytest_plugins = "sphinx.testing.fixtures"  # pylint: disable=invalid-name


# Inspired from https://github.com/mansenfranzen/autodoc_pydantic/blob/1d14f120373e481023de889711210f4d2a2b853c/tests/conftest.py


@pytest.fixture(scope="session")
def rootdir() -> Path:
    return Path(__file__).parent.resolve() / "test-docs"


def do_autodoc(
    app: Sphinx,
    documenter: str,
    object_path: str,
    options_doc: Optional[Dict] = None,
) -> List[str]:
    """Run auto `documenter` for given object referenced by `object_path`
    within provided sphinx `app`. Optionally override app and documenter
    settings.

    Parameters
    ----------
    app: sphinx.application.Sphinx
        Sphinx app in which documenter is run.
    documenter: str
        Name of documenter which is used to document `object_path`.
    object_path: str
        Full path to object to be documented.
    options_doc: dict
        Optional settings to be passed to documenter.

    Returns
    -------
    result: list
        List of strings containing lines of generated restructured text.

    """

    # configure app
    app.env.temp_data.setdefault("docname", "index")  # set dummy docname

    # get documenter and its options
    options_doc = options_doc or {}
    doc_cls = app.registry.documenters[documenter]
    doc_opts = process_documenter_options(doc_cls, app.config, options_doc)

    # get documenter bridge which is going to contain the result
    state = Mock()
    state.document.settings.tab_width = 8
    bridge = DocumenterBridge(app.env, LoggingReporter(""), doc_opts, 1, state)

    # instaniate documenter and run
    documenter = doc_cls(bridge, object_path)  # type: ignore[assignment]
    documenter.generate()  # type: ignore[attr-defined]

    return list(bridge.result)


@pytest.fixture(scope="function")
def test_app(make_app, sphinx_test_tempdir, rootdir):
    """Create callable which returns a fresh sphinx test application. The test
    application is faster than using a production application (like `prod_app`
    fixture).

    This fixture is mainly used to test generated rst (via `autodocument`
    fixture) and generated docutils (via `parse_rst` fixture).

    When testing the production behaviour including all functionality, please
    use `prod_app`.

    """

    def create(
        testroot: str,
        conf: Optional[Dict] = None,
    ):
        srcdir = sphinx_test_tempdir / testroot
        shutil.rmtree(srcdir, ignore_errors=True)

        if rootdir and not srcdir.exists():
            testroot_path = rootdir / ("test-" + testroot)
            shutil.copytree(testroot_path, srcdir)

        kwargs = {"srcdir": srcdir, "confoverrides": {}}

        if conf:
            kwargs["confoverrides"].update(conf)
        return make_app("html", **kwargs)

    return create


@pytest.fixture(scope="function")
def autodocument(test_app):
    """Main fixture to test generated reStructuredText from given object path
    with provided auto-documenter while optionally allowing to overwriting
    sphinx app settings `options_app` and auto-documenter directive settings
    `options_doc`.

    Parameters
    ----------
    documenter: str
        Name of the auto-documenter to be used to generate rst.
    object_path: str
        Fully qualified path to the relevant python object to be documented.
    options_doc: dict, optional
        Overwrite auto-documenter directive settings.
    options_app: dict, optional
        Overwrite sphinx app settings.
    testroot: str, optional
        Name of the sphinx test source directory which are located under
        `autodoc_pydantic/tests/roots/`. By default, it uses the `base`
        directory.

    """

    # pylint: disable=too-many-arguments
    def _auto(
        documenter: str,
        object_path: str,
        options_doc: Optional[Dict] = None,
        options_app: Optional[Dict] = None,
        testroot: str = "base",
    ):
        app = test_app(testroot, conf=options_app)

        return do_autodoc(
            app=app,
            documenter=documenter,
            object_path=object_path,
            options_doc=options_doc,
        )

    return _auto
