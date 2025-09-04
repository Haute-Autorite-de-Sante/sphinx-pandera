import pandera.pandas as pa
from pandera.typing.pandas import Index


class TestSingleIndexModel(pa.DataFrameModel):
    """
    Model with a single field which is a pandas index
    """

    # pylint: disable=too-few-public-methods
    class Config:
        strict = True
        coerce = True

    key: Index[str] = pa.Field(
        unique=True,
        check_name=True,
        str_matches=r"^AIPE-[0-9]+$",
        title="Firsti Index type field",
        description="Field whose dtype is Index",
    )


class TestMultiIndexModel(pa.DataFrameModel):
    """
    Model with two fields which are a pandas index (multiIndex)
    """

    # pylint: disable=too-few-public-methods
    class Config:
        strict = True
        coerce = True

    key1: Index[str] = pa.Field(
        unique=True,
        check_name=True,
        str_matches=r"^AIPE-[0-9]+$",
        title="First Index type field",
        description="Field whose dtype is Index",
    )

    key2: Index[str] = pa.Field(
        unique=True,
        check_name=True,
        str_matches=r"^AIPE2-[0-9]+$",
        title="Second Index type field",
        description="Field whose dtype is Index",
    )
