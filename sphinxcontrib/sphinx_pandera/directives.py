from typing import Tuple

from docutils import nodes
from docutils.nodes import Text
from docutils.parsers.rst.directives import unchanged
from sphinx.addnodes import desc_annotation, desc_sig_space, desc_signature
from sphinx.domains.python import PyAttribute, PyClasslike, PyMethod, py_sig_re

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


class PanderaModel(PanderaDirectiveBase, PyClasslike):  # type: ignore
    """Specialized directive for pandera models."""

    # CLEANUP: doesn't seem useful to generate proper doc
    # option_spec = PyClasslike.option_spec.copy()
    # option_spec.update(
    #     {
    #         "members": None,
    #     }
    # )

    config_name = "model"
    default_prefix = "class"


class PanderaField(PanderaDirectiveBase, PyAttribute):  # type: ignore
    """Specialized directive for pandera fields."""

    option_spec = PyAttribute.option_spec.copy()  # type: ignore[misc]
    option_spec.update(
        {
            # CLEANUP: doesn't seem useful to generate proper doc
            # "field-signature-prefix": unchanged,
            "title": unchanged,
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

        title = self.options.get("title")
        if title is not None:
            signode += desc_annotation("", f", {title}")

        return fullname, prefix


class PanderaCheck(PanderaDirectiveBase, PyMethod):  # type: ignore
    # CLEANUP: doesn't seem useful to generate proper doc
    # option_spec = PyMethod.option_spec.copy()
    # option_spec.update(
    #     {
    #         "check-signature-prefix": unchanged,
    #     }
    # )

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
            if node.tagname == "desc_parameterlist"  # type: ignore
        ]:
            signode.children.remove(remove)
        return fullname, prefix

    def before_content(self) -> None:
        # HACK: 1/2 disable parameters and return type sections
        self.typehints_config_save = self.env.app.config.autodoc_typehints
        self.env.app.config.autodoc_typehints = None  # type: ignore
        return super().before_content()

    def after_content(self) -> None:
        # HACK: 2/2 disable parameters and return type sections
        self.env.app.config.autodoc_typehints = self.typehints_config_save  # type: ignore
        return super().after_content()
