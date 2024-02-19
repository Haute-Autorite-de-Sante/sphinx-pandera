import inspect
from typing import Any, Optional, Tuple

import pandera as pa
from docutils import nodes
from docutils.nodes import Text
from docutils.parsers.rst.directives import unchanged
from docutils.statemachine import StringList
from sphinx.addnodes import desc_annotation, desc_sig_space, desc_signature
from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx.domains.python import PyAttribute, PyClasslike, PyMethod, py_sig_re
from sphinx.ext.autodoc import (
    AttributeDocumenter,
    ClassDocumenter,
    MethodDocumenter,
)
from sphinx.ext.autodoc.directive import DocumenterBridge
from sphinx.util.docstrings import prepare_docstring

TupleStr = Tuple[str, str]


# LATER:
# validators/checks autodocumenter
#    - [x] basic stuff
#    - [x] cross href fields <=> checks
#    - [x] Remove parameters section &co
#    - [ ] Dataframe-level validators
#    - [x] source tags
#    - [x] le, ge, str_matches
#    - [ ] document field categories
#    - [ ] metadata
# Global config class
#    - [ ] basic stuff
# linting


def setup(app: Sphinx) -> dict:
    add_configuration_values(app)

    app.add_directive_to_domain("py", "pandera_check", PanderaCheck)
    app.add_directive_to_domain("py", "pandera_field", PanderaField)
    app.add_directive_to_domain("py", "pandera_model", PanderaModel)

    app.setup_extension("sphinx.ext.autodoc")  # Require autodoc extension

    app.add_autodocumenter(PanderaCheckDocumenter)
    app.add_autodocumenter(PanderaFieldDocumenter)
    app.add_autodocumenter(PanderaModelDocumenter)
    add_domain_object_types(app)

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


##############
# DIRECTIVES #
##############
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

    option_spec = PyClasslike.option_spec.copy()
    option_spec.update(
        {
            "model-signature-prefix": unchanged,
        }
    )

    config_name = "model"
    default_prefix = "class"


class PanderaField(PanderaDirectiveBase, PyAttribute):  # type: ignore
    """Specialized directive for pandera fields."""

    option_spec = PyAttribute.option_spec.copy()
    option_spec.update(
        {
            "field-signature-prefix": unchanged,
            "title": unchanged,
        }
    )

    config_name = "field"
    default_prefix = "attribute"

    def get_field_name(self, sig: str) -> str:
        """Get field name from signature. Borrows implementation from
        `PyObject.handle_signature`.

        """

        return py_sig_re.match(sig).groups()[1]

    def handle_signature(self, sig: str, signode: desc_signature) -> TupleStr:
        """add field title"""
        fullname, prefix = super().handle_signature(sig, signode)

        title = self.options.get("title")
        if title is not None:
            signode += desc_annotation("", f", {title}")

        return fullname, prefix


class PanderaCheck(PanderaDirectiveBase, PyMethod):  # type: ignore
    option_spec = PyMethod.option_spec.copy()
    option_spec.update(
        {
            "check-signature-prefix": unchanged,
        }
    )

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


##############
# Documenters #
##############

#########
# Model #
#########


class PanderaModelDocumenter(ClassDocumenter):
    objtype = "pandera_model"

    directivetype = "pandera_model"

    priority = 10 + ClassDocumenter.priority

    option_spec = dict(ClassDocumenter.option_spec)

    pyautodoc_pass_to_directive = ("model-signature-prefix",)

    pyautodoc_set_default_option = ("member-order", "undoc-members", "members")

    pyautodoc_prefix = "model"

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        try:
            is_val = super().can_document_member(
                member, membername, isattr, parent
            )
            is_model = issubclass(member, pa.DataFrameModel)
            if is_val and is_model:
                # HACK: don't remove this call, it caches the imports
                # so that the field documenter can work properly downstream
                # there is some type handling that intercepts things
                # in a weird way
                member.to_schema()
            return is_val and is_model

        except TypeError:
            return False

    def format_signature(self, **kwargs) -> str:
        """
        hide class arguments
        """
        return ""


#########
# Field #
#########


class PanderaFieldDocumenter(AttributeDocumenter):
    """Represents specialized Documenter subclass for pandera fields."""

    # pylint: disable=too-many-ancestors

    objtype = "pandera_field"
    directivetype = "pandera_field"
    priority = 10 + AttributeDocumenter.priority
    option_spec = dict(AttributeDocumenter.option_spec)
    option_spec.update(
        {
            "title": unchanged,
        }
    )
    member_order = 0

    pyautodoc_pass_to_directive = ("field-signature-prefix",)

    def __init__(
        self, directive: DocumenterBridge, name: str, indent: str = ""
    ) -> None:
        super().__init__(directive, name, indent)
        self.pandera_schema = None

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """Filter only pandera fields."""

        is_valid = super().can_document_member(
            member, membername, isattr, parent
        )
        try:
            if not issubclass(parent.object, pa.DataFrameModel):
                return False
        except TypeError:
            return False
        # pylint: disable-next=protected-access
        is_field = membername in parent.object._get_model_attrs()

        return is_valid and is_field

    @property
    def pandera_field_name(self) -> str:
        """Provide the pandera field name which refers to the member name of
        the parent pandera model.

        """
        return self.objpath[-1]

    def add_directive_header(self, sig: str) -> None:
        """Delegate header options."""
        # Call works only here
        super().add_directive_header(sig)

        self.add_title()

    @property
    def pandera_field(self) -> pa.Field:  # type: ignore
        """
        Get pandera field
        """
        # pylint: disable-next=protected-access
        return self.parent._get_model_attrs()[self.pandera_field_name]

    def add_content(
        self,
        more_content: Optional[StringList],
        **kwargs,
    ) -> None:
        """Delegate additional content creation."""
        super().add_content(more_content, **kwargs)
        self.pandera_schema = self.parent.to_schema()
        self.add_description()
        self.add_constraints()
        self.add_checks()

    def add_title(self):
        """Add title option for field directive"""

        if not self.pandera_field.title:
            return
        sourcename = self.get_sourcename()
        self.add_line(f"   :title: {self.pandera_field.title}", sourcename)

    def add_description(self):
        """Adds description from schema if present."""
        description = self.pandera_field.description

        if not description:
            return
        tabsize = self.directive.state.document.settings.tab_width
        lines = prepare_docstring(description, tabsize=tabsize)
        source_name = self.get_sourcename()

        for line in lines:
            self.add_line(line, source_name)
        self.add_line("", source_name)

    def add_constraints(self):
        """
        Adds section showing all defined constraints.
        """
        constraints = {
            "nullable": self.pandera_field.nullable,
            "unique": self.pandera_field.unique,
            "coerce": self.pandera_field.coerce,
        }

        source_name = self.get_sourcename()
        self.add_line(":Constraints:", source_name)
        for key, value in constraints.items():
            line = f"   - **{key}** = {value}"
            self.add_line(line, source_name)

    def get_check_func_ref(self, check):
        # 1. find func obj from name
        # 2. build ref
        obj = getattr(self.parent, check.name)
        module = inspect.getmodule(obj)

        return f"{module.__name__}.{self.parent}.{check.name}"

    def add_checks(self):
        """
        Adds section showing all checks
        """
        checks = self.pandera_schema.columns[self.pandera_field_name].checks

        if not checks:
            return

        source_name = self.get_sourcename()
        self.add_line(":Validated by:", source_name)
        for check in checks:
            # HACK: standard checks implement nice error message
            if check.error:
                line = f"   - **{check.error}**"
            else:
                ref = self.get_check_func_ref(check)
                line = f"   - :py:obj:`{check.name} <{ref}>`"
            self.add_line(line, source_name)


#########
# Check #
#########
class PanderaCheckDocumenter(MethodDocumenter):
    """
    Documents Pandera checks on columns/dataframe
    """

    objtype = "pandera_check"
    directivetype = "pandera_check"
    member_order = 50
    priority = 10 + MethodDocumenter.priority
    option_spec = MethodDocumenter.option_spec.copy()

    pyautodoc_pass_to_directive = ("check-signature-prefix",)

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """Filter only pandera fields."""

        is_valid = super().can_document_member(
            member, membername, isattr, parent
        )
        try:
            if not issubclass(parent.object, pa.DataFrameModel):
                return False
        except TypeError:
            return False
        # pylint: disable-next=protected-access
        model_attrs = parent.object._get_model_attrs()

        is_check = membername in model_attrs and isinstance(
            model_attrs[membername], classmethod
        )

        return is_valid and is_check

    def get_checked_columns(self):
        schema: pa.DataFrameSchema = self.parent.to_schema()
        columns = []
        for _, column in schema.columns.items():
            for check in column.checks:
                # HACK: fragile to multiple classes having the same method
                if check.name == self.name.rsplit(".", 1)[-1]:
                    columns.append(column)

        return columns

    def get_column_func_ref(self, column):
        module = inspect.getmodule(self.parent)

        return f"{module.__name__}.{self.parent}.{column.name}"

    def add_content(
        self, more_content: Optional[StringList], **kwargs
    ) -> None:
        """
        Adds content to the check section
        """

        super().add_content(more_content, **kwargs)

        self.add_columns_list()

    def add_columns_list(self):
        """
        Adds fields list
        """
        checked_columns = self.get_checked_columns()

        if not checked_columns:
            return

        source_name = self.get_sourcename()
        self.add_line(":Validates:", source_name)

        for column in checked_columns:
            ref = self.get_column_func_ref(column)
            line = f"   - :py:obj:`{column.name} <{ref}>`"
            self.add_line(line, source_name)

        self.add_line("", source_name)
