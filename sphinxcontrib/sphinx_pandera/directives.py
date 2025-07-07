from typing import Tuple

from docutils import nodes
from docutils.nodes import Text
from docutils.parsers.rst.directives import unchanged
from sphinx.addnodes import desc_annotation, desc_sig_space, desc_signature
from sphinx.domains.python import (
    PyAttribute,
    PyClasslike,
    PyMethod,
    PyVariable,
    py_sig_re,
)

TupleStr = Tuple[str, str]


class PanderaDirectiveBase:
    """Base class for pandera directive providing common functionality."""

    # pylint: disable=too-few-public-methods

    config_name: str
    default_prefix: str

    def __init__(self, *args):
        super().__init__(*args)

    def get_signature_prefix(self, _: str) -> list[nodes.Node]:
        """Overwrite original signature prefix with custom pandera ones."""
        config_name = f"sphinx_pandera_{self.config_name}_signature_prefix"
        # pylint: disable-next=no-member
        prefix = getattr(self.env.config, config_name, None)  # type: ignore
        value = prefix or self.default_prefix

        return [Text(value), desc_sig_space()]


class PanderaSchema(PanderaDirectiveBase, PyVariable):  # type: ignore
    """Specialized directive for pandera models."""

    config_name = "schema"
    # default_prefix = "class"

    def handle_signature(self, sig: str, signode: desc_signature) -> TupleStr:
        """Removes variable value from signature"""
        # HACK
        self.options["value"] = False
        fullname, prefix = super().handle_signature(sig, signode)

        return fullname, prefix


class PanderaModel(PanderaDirectiveBase, PyClasslike):  # type: ignore
    """Specialized directive for pandera models."""

    config_name = "model"
    default_prefix = "class"


class PanderaModelConfig(PanderaDirectiveBase, PyClasslike):  # type: ignore
    """Specialized directive for pandera model configs."""

    config_name = "model_config"
    default_prefix = "class"


class PanderaField(PanderaDirectiveBase, PyAttribute):  # type: ignore
    """Specialized directive for pandera fields."""

    option_spec = PyAttribute.option_spec.copy()  # type: ignore[misc]
    option_spec.update(
        {
            "title": unchanged,  # to display field title property
        }
    )

    config_name = "field"
    default_prefix = "attribute"

    def get_field_name(self, sig: str) -> str:
        """Get field name from signature. Borrows implementation from
        `PyObject.handle_signature`.

        """
        return py_sig_re.match(sig).groups()[1]  # type: ignore[union-attr]

    def handle_signature(self, sig: str, signode: desc_signature) -> TupleStr:
        """add field title"""
        fullname, prefix = super().handle_signature(sig, signode)

        # HACK: pop module/variable name from field signature for pandera schema
        if "." in signode[1].astext():
            signode.pop(1)
        title = self.options.get("title")
        if title is not None:
            signode += desc_annotation("", f", {title}")

        return fullname, prefix


class PanderaCheck(PanderaDirectiveBase, PyMethod):  # type: ignore

    config_name = "check"
    default_prefix = "classmethod"

    def __init__(self, *args):
        super().__init__(*args)  #
        self.typehints_config_save = None

    def handle_signature(self, sig: str, signode: desc_signature) -> TupleStr:
        """
        Remove method parameters
        """

        fullname, prefix = super().handle_signature(sig, signode)
        for remove in [
            node
            for node in signode.children
            if node.tagname in {"desc_parameterlist", "desc_returns"}  # type: ignore
        ]:
            signode.children.remove(remove)
        return fullname, prefix
