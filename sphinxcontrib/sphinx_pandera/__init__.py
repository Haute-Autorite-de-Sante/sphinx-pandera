"""Sphinx Pandera."""

from sphinx.application import Sphinx

from sphinxcontrib.sphinx_pandera.directives import (
    PanderaCheck,
    PanderaField,
    PanderaModel,
    PanderaModelConfig,
    PanderaSchema,
)
from sphinxcontrib.sphinx_pandera.documenters import (
    PanderaCheckDocumenter,
    PanderaFieldDocumenter,
    PanderaModelConfigDocumenter,
    PanderaModelDocumenter,
    PanderaSchemaDocumenter,
)


def setup(app: Sphinx) -> dict:
    add_configuration_values(app)

    app.add_directive_to_domain("py", "pandera_check", PanderaCheck)
    app.add_directive_to_domain("py", "pandera_field", PanderaField)
    app.add_directive_to_domain("py", "pandera_model", PanderaModel)
    app.add_directive_to_domain("py", "pandera_schema", PanderaSchema)
    app.add_directive_to_domain(
        "py", "pandera_model_config", PanderaModelConfig
    )

    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension

    app.add_autodocumenter(PanderaCheckDocumenter)
    app.add_autodocumenter(PanderaFieldDocumenter)
    app.add_autodocumenter(PanderaModelDocumenter)
    app.add_autodocumenter(PanderaSchemaDocumenter)
    app.add_autodocumenter(PanderaModelConfigDocumenter)

    return {
        "version": "0.0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def add_configuration_values(app: Sphinx):
    stem = "sphinx_pandera_"

    app.add_config_value(
        f"{stem}model_signature_prefix", "pandera model", "env", str
    )

    app.add_config_value(
        f"{stem}schema_signature_prefix", "pandera schema", "env", str
    )

    app.add_config_value(f"{stem}field_signature_prefix", "column", "env", str)

    app.add_config_value(f"{stem}check_signature_prefix", "check", "env", str)
