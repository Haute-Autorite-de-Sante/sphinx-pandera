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
    ObjectMember,
    get_class_members,
)
from sphinx.ext.autodoc.directive import DocumenterBridge
from sphinx.util.docstrings import prepare_docstring

##########
# Schema #
##########


class PanderaSchemaDocumenter(DataDocumenter):
    objtype = "pandera_schema"
    directivetype = "pandera_schema"

    priority = 10 + DataDocumenter.priority

    option_spec = dict(DataDocumenter.option_spec)

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        try:
            is_val = super().can_document_member(
                member, membername, isattr, parent
            )
            is_model = issubclass(member, pa.DataFrameSchema)
            return is_val and is_model

        except TypeError:
            return False

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
            self.add_field(field, source_name)

        if isinstance(self.object.index, pa.MultiIndex):
            indices = self.object.index.named_indexes
        else:
            indices = {self.object.index.name: self.object.index}

        for idx_name, idx in indices.items():
            # HACK: this determines if an index will be documented or not
            # We should find a better way to identify if the index was specified
            # explicitely in the schema
            if idx.name is not None:
                self.add_field(idx, idx_name, is_index=True)

    def add_field(self, field, source_name, is_index=False):
        """
        Adds a field with custom prefix if the field is an index
        """

        self.add_line(
            f".. py:pandera_field:: {'.'.join(self.objpath)}.{field.name}",
            source_name,
        )

        if is_index:
            self.add_line(f"   :type: Index[{field.dtype }]", source_name)
        else:
            self.add_line(f"   :type: {field.dtype }", source_name)
        if field.title is not None:
            self.add_line(f"   :title: {field.title}", source_name)

        constraints = {
            "nullable": field.nullable,
            "unique": field.unique,
            "coerce": field.coerce,
        }

        try:
            constraints["required"] = field.required
        except AttributeError:  # Field is an Index or MultiIndex
            constraints["required"] = "True (Index)"

        if field.description is not None:
            self.add_line("", source_name)
            self.add_line(f"   {field.description}", source_name)

        self.add_line("", source_name)
        self.add_line("   :Constraints:", source_name)
        for key, value in constraints.items():
            self.add_line(f"      - **{key}** = {value}", source_name)

        self.add_line("", source_name)

        if not field.checks:
            return

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
        for field in list(self.object.columns.values()) + [self.object.index]:
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
            self.object.to_schema()
        return ret

    @classmethod
    def can_document_member(
        cls, member: Any, membername: str, isattr: bool, parent: Any
    ) -> bool:
        try:
            is_val = super().can_document_member(
                member, membername, isattr, parent
            )
            is_model = issubclass(member, pa.DataFrameModel)
            return is_val and is_model

        except TypeError:
            return False

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
        try:
            is_val = super().can_document_member(
                member, membername, isattr, parent
            )
            is_model_config = ("Config" in parent.object.__dict__) and (
                getattr(member, "__name__", "") == "Config"
            )

            return is_val and is_model_config

        except TypeError:
            return False

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
            return self.pandera_schema.columns[self.object]
        except KeyError as exc:
            idx = self.pandera_schema.index
            if isinstance(idx, pa.Index) and (idx.name == self.object):
                return idx
            if isinstance(idx, pa.MultiIndex):
                return self.pandera_schema.index.named_indexes[self.object]
            raise NotImplementedError(
                f"Unsupported field type for field {self.object}"
            ) from exc

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
        except AttributeError:  # Field is an Index or MultiIndex
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
        module = inspect.getmodule(obj)

        return f"{module.__name__}.{self.parent}.{check.name}"

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
