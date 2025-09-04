import inspect
from typing import Any, List, Optional

import pandera.pandas as pa
from docutils.parsers.rst.directives import unchanged
from docutils.statemachine import StringList
from sphinx.ext.autodoc import (
    ALL,
    AttributeDocumenter,
    ClassDocumenter,
    DataDocumenter,
    MethodDocumenter,
    ModuleDocumenter,
    ObjectMember,
    get_class_members,
)
from sphinx.ext.autodoc.directive import DocumenterBridge
from sphinx.util.docstrings import prepare_docstring
from sphinxcontrib.sphinx_pandera.inspection import ModelInspector

##########
# Schema #
##########


class PanderaSchemaDocumenter(DataDocumenter):
    """
    Documenter for pandera Schema models. Schemas are not classes, but instances.
    Note that a Model (a class) can be converted to a Schema (an instance) using ``.to_schema()``
    """
    objtype = "pandera_schema"
    directivetype = "pandera_schema"

    priority = 10 + DataDocumenter.priority

    option_spec = dict(DataDocumenter.option_spec)

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:

        is_val = super().can_document_member(member, membername, isattr, parent)
        is_schema = ModelInspector.is_pandera_schema(member)

        # HACK to avoid checking for `is_val` when this is a schema. Indeed `isattr` seems to be false for package data
        if is_schema:
            if not is_val:
                is_val = isinstance(parent, ModuleDocumenter)

        return is_schema and is_val

    def add_content(  # pylint: disable=unused-argument
        self,
        more_content: Optional[StringList],
        **kwargs,
    ) -> None:
        """Delegate additional content creation."""
        self.add_title()
        self.add_description()
        self.add_config()
        self.add_fields()
        self.add_field_validators()
        self.add_schema_validators()

    def add_title(self):
        if not self.object.title:
            return
        self.add_line(f"   :title: {self.object.title}", self.get_sourcename())

    def add_description(self):
        """Adds description from schema if present."""
        description = self.object.description

        if not description:
            return
        tabsize = self.directive.state.document.settings.tab_width
        lines = prepare_docstring(description, tabsize=tabsize)
        source_name = self.get_sourcename()

        for line in lines:
            self.add_line(line, source_name)
        self.add_line("", source_name)

    def add_config(self):
        """
        Adds schema level configuration
        """
        source_name = self.get_sourcename()
        self.add_line(":Schema Configuration:", source_name)
        config = {
            "coerce": self.object.coerce,
            "ordered": self.object.ordered,
            "strict": self.object.strict,
        }
        for key, value in config.items():
            self.add_line(f"      - **{key}** = {value}", source_name)
        self.add_line("", source_name)

    def add_fields(self):
        """
        Adds fields description
        """
        source_name = self.get_sourcename()
        for field in self.object.columns.values():
            self.add_line(
                f".. py:pandera_field:: {'.'.join(self.objpath)}.{field.name}",
                source_name,
            )
            self.add_line(f"   :type: {field.dtype}", source_name)
            if field.title is not None:
                self.add_line(f"   :title: {field.title}", source_name)

            constraints = {
                "nullable": field.nullable,
                "unique": field.unique,
                "coerce": field.coerce,
                "required": field.required,
            }

            if field.description is not None:
                self.add_line("", source_name)
                self.add_line(f"   {field.description}", source_name)

            self.add_line("", source_name)
            self.add_line("   :Constraints:", source_name)
            for key, value in constraints.items():
                self.add_line(f"      - **{key}** = {value}", source_name)

            self.add_line("", source_name)

            if not field.checks:
                continue

            source_name = self.get_sourcename()
            self.add_line("   :Validated by:", source_name)
            for check in field.checks:
                # HACK: standard checks implement nice error message
                if check.error:
                    line = f"      - **{check.error}**"
                else:
                    ref = f"{self.modname}.{check.name}"
                    line = f"      - :py:obj:`{check.name} <{ref}>`"
                self.add_line(line, source_name)

            self.add_line("", source_name)

    def add_field_validators(self):
        """
        Add custom field validators
        """
        field_validators = {}
        source_name = self.get_sourcename()
        for field in self.object.columns.values():
            for check in field.checks:
                # HACK: standard checks implement nice error message
                if check.error:
                    continue
                check_d = field_validators.setdefault(
                    check.name,
                    {
                        "doc": check._check_fn.__doc__.strip(),  # pylint: disable=protected-access
                        "fields": [],
                    },
                )
                check_d["fields"].append(field.name)

        for check_name, check_d in field_validators.items():
            self.add_line(f".. py:pandera_check:: {check_name}", source_name)
            self.add_line("", source_name)
            self.add_line(f"   {check_d['doc']}", source_name)
            self.add_line("", source_name)
            self.add_line("   :Validates:", source_name)

            for field in check_d["fields"]:
                self.add_line(f"      - :py:obj:`{field}`", source_name)

        self.add_line("", source_name)

    def add_schema_validators(self):
        """
        Add custom schema validators
        """
        source_name = self.get_sourcename()
        if not self.object.checks:
            return

        for check in self.object.checks:
            self.add_line(
                f".. py:pandera_check:: {check.__name__}", source_name
            )
            self.add_line("", source_name)
            self.add_line(f"   {check.__doc__.strip()}", source_name)


#########
# Model #
#########


class PanderaModelDocumenter(ClassDocumenter):
    objtype = "pandera_model"

    directivetype = "pandera_model"

    priority = 10 + ClassDocumenter.priority

    option_spec = dict(ClassDocumenter.option_spec)

    def import_object(self, raiseerror: bool = False) -> bool:
        ret = super().import_object(raiseerror)
        # HACK: don't remove this call, it caches the imports
        # so that the field documenter can work properly downstream
        # there is some type handling that intercepts things
        # in a weird way
        if self.object:
            # Convert pandera Model (class) to Schema (instance) so that it can be handled by PanderaSchemaDocumenter
            self.object.to_schema()
        return ret

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """Filter only pandera models"""

        is_val = super().can_document_member(member, membername, isattr, parent)
        is_model = ModelInspector.is_pandera_model(member)
        return is_val and is_model

    def document_members(self, *args, **kwargs) -> None:
        self.options["members"] = ALL
        self.options["undoc-members"] = ALL
        self.options["member-order"] = "bysource"

        super().document_members(*args, **kwargs)

    def format_signature(self, **kwargs) -> str:
        """
        hide class arguments
        """
        return ""


#########
# Model Config #
#########


class PanderaModelConfigDocumenter(ClassDocumenter):
    objtype = "pandera_model_config"

    directivetype = "pandera_model_config"

    priority = 10 + ClassDocumenter.priority

    option_spec = dict(ClassDocumenter.option_spec)

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        is_val = super().can_document_member(member, membername, isattr, parent)
        is_model_config = ModelInspector.is_pandera_model_config(member, parent.object)
        return is_val and is_model_config

    def get_object_members(
        self, want_all: bool
    ) -> tuple[bool, List[ObjectMember]]:
        members = get_class_members(
            self.object,
            self.objpath,
            self.get_attr,
            self.config.autodoc_inherit_docstrings,
        )

        return False, [
            m
            for k, m in members.items()
            if k in ["strict", "coerce", "ordered"]
        ]

    def add_content(
        self,
        more_content: Optional[StringList],
        **kwargs,
    ) -> None:
        """Delegate additional content creation."""
        super().add_content(more_content, **kwargs)

    def format_signature(self, **kwargs) -> str:
        """
        hide class arguments
        """
        return ""


#########
# Field #
#########


# pylint: disable=abstract-method
class PanderaFieldDocumenter(AttributeDocumenter):
    """Represents specialized Documenter subclass for pandera fields."""

    # pylint: disable=too-many-ancestors

    objtype = "pandera_field"
    directivetype = "pandera_field"
    priority = 10 + AttributeDocumenter.priority
    option_spec = dict(AttributeDocumenter.option_spec)
    option_spec.update({"title": unchanged})
    member_order = 0

    pyautodoc_pass_to_directive = ("field-signature-prefix",)

    def __init__(
        self, directive: DocumenterBridge, name: str, indent: str = ""
    ) -> None:
        super().__init__(directive, name, indent)
        self._pandera_schema = None

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        """Filter only pandera fields."""

        is_valid = super().can_document_member(member, membername, isattr, parent)
        is_field = ModelInspector.is_pandera_field(parent=parent.object, field_name=membername)
        return is_valid and is_field  # and isattr

    @property
    def pandera_schema(self) -> pa.DataFrameSchema:
        """Provide the pandera field name which refers to the member name of
        the parent pandera model.

        """
        if self._pandera_schema is None:
            self._pandera_schema = self.parent.to_schema()
        return self._pandera_schema  # type: ignore

    @property
    def pandera_field_name(self) -> str:
        """Provide the pandera field name which refers to the member name of
        the parent pandera model.

        """
        return self.objpath[-1]

    def add_directive_header(self, sig: str) -> None:
        """Delegate header options."""
        # Call works only here
        self.options.no_value = True  # type: ignore
        super().add_directive_header(sig)

        self.add_title()

    @property
    def pandera_field(self) -> pa.Field:  # type: ignore
        """
        Get pandera field
        """
        try:
            # A Column ?
            return self.pandera_schema.columns[self.object]
        except KeyError as e:
            # GH#5 - TODO still needed ?
            # This might be the Index !
            idx = self.pandera_schema.index
            if idx.name == self.object:
                return idx
            raise e from e

    def add_content(
        self,
        more_content: Optional[StringList],
        **kwargs,
    ) -> None:
        """Delegate additional content creation."""

        super().add_content(more_content, **kwargs)
        self.add_description()
        self.add_constraints()
        self.add_checks()

    def add_title(self):
        """Add title option for field directive"""
        if not self.pandera_field.title:
            return
        sourcename = self.get_sourcename()
        self.add_line(
            f"   :title: {self.pandera_field.title}",
            sourcename,
        )

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
        try:
            constraints["required"] = self.pandera_field.required
        except AttributeError:
            # GH#5 - TODO still needed ?
            constraints["required"] = "True (Index)"

        source_name = self.get_sourcename()
        self.add_line(":Constraints:", source_name)
        for key, value in constraints.items():
            line = f"   - **{key}** = {value}"
            self.add_line(line, source_name)

    def get_check_func_ref(self, check):
        # 1. find func obj from name
        # 2. build ref
        obj = getattr(self.parent, check.name)
        # module = inspect.getmodule(obj)

        # Rely on self (the FieldDocumenter instance)'s module name instead of `inspect.getmodule`
        # So that the cross-reference will work if the symbol is imported by autodoc
        # from an __init__.py instead of the full module path.
        return f"{self.modname}.{obj.__qualname__}"

    def add_checks(self):
        """
        Adds section showing all checks
        """
        checks = self.pandera_field.checks

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

        is_valid = super().can_document_member(member, membername, isattr, parent)
        is_check = ModelInspector.is_checker_by_name(membername, parent.object)
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
        # module = inspect.getmodule(self.parent)

        # obj = self.parent._get_model_attrs()[column.name]

        # Rely on self (the CheckDocumenter instance)'s module name instead of `inspect.getmodule`
        # So that the cross-reference will work if the symbol is imported by autodoc
        # from an __init__.py instead of the full module path.
        return f"{self.modname}.{self.parent}.{column.name}"  # {obj.__qualname__}"

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
