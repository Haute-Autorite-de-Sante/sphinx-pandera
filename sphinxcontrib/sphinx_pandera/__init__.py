"""Sphinx Pandera."""

from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx_pandera.directives import PanderaCheck, PanderaField, PanderaModel
from sphinx_pandera.documenters import (
    PanderaCheckDocumenter,
    PanderaFieldDocumenter,
    PanderaModelDocumenter,
)


def setup(app: Sphinx) -> dict:
    add_configuration_values(app)

    app.add_directive_to_domain("py", "pandera_check", PanderaCheck)
    app.add_directive_to_domain("py", "pandera_field", PanderaField)
    app.add_directive_to_domain("py", "pandera_model", PanderaModel)

    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension

    app.add_autodocumenter(PanderaCheckDocumenter)
    app.add_autodocumenter(PanderaFieldDocumenter)
    app.add_autodocumenter(PanderaModelDocumenter)
    # CLEANUP: doesn't seem useful to generate proper doc
    # add_domain_object_types(app)

    return {
        "version": "0.0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def add_configuration_values(app: Sphinx):
    stem = "sphinx_pandera_"

    app.add_config_value(
        f"{stem}model_signature_prefix", "pandera model", True, str
    )

    app.add_config_value(f"{stem}field_signature_prefix", "column", True, str)

    app.add_config_value(f"{stem}check_signature_prefix", "check", True, str)


# CLEANUP: doesn't seem useful to generate proper doc
def add_domain_object_types(app: Sphinx):
    """Hack to add object types to already instantiated python domain since
    `add_object_type` currently only works for std domain.

    """

    object_types = app.registry.domain_object_types.setdefault("py", {})

    obj_types_mapping = {
        # ("field", "validator", "config"): ("obj", "any"),
        # ("model", "settings"): ("obj", "any", "class"),
        ("field",): ("obj", "any"),
        ("model",): ("obj", "any", "class"),
    }

    for obj_types, roles in obj_types_mapping.items():
        for obj_type in obj_types:
            object_types[f"[pandera]_{obj_type}"] = ObjType(obj_type, *roles)
