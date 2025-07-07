"""This module contains the inspection functionality for pandera models. It
is used to retrieve relevant information about fields, checkers, config and
schema of pandera models.

"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import pandera as pa


class ModelInspector:
    """Provides static analysis methods to check if an object is a certain pandera kind of object"""

    @staticmethod
    def is_pandera_model(obj: Any) -> bool:
        """Determine if object is a valid pandera model."""

        try:
            return isinstance(obj, pa.api.base.model.MetaModel)
        except TypeError:
            return False

    @staticmethod
    def is_pandera_schema(obj: Any) -> bool:
        """Determine if object is a valid pandera model."""

        try:
            return isinstance(obj, pa.api.base.schema.BaseSchema)
        except TypeError:
            return False

    @staticmethod
    def is_pandera_model_config(obj: Any, parent:Any) -> bool:
        return (
            (parent is not None)
            and ("Config" in getattr(parent, "__dict__", {}))
            and (getattr(obj, "__name__", "") == "Config")
        )

    @classmethod
    def is_pandera_field(cls, parent: Any, field_name: str) -> bool:  # noqa: ANN401
        """Determine if given `field` is a pandera field."""

        if not cls.is_pandera_model(parent):
            return False

        # return field_name in parent.model_fields
        return field_name in parent._get_model_attrs()

    @classmethod
    def is_checker_by_name(cls, name: str, obj: Any) -> bool:  # noqa: ANN401
        """Determine if a checker is present under provided `name` for given
        `model`.

        """

        if cls.is_pandera_model(obj):
            # inspector = ModelInspector(obj)
            # return name in inspector.checkers.names

            # pylint: disable-next=protected-access
            model_attrs = obj._get_model_attrs()
            is_check = name in model_attrs and isinstance(model_attrs[name], classmethod)
            return is_check

        return False

