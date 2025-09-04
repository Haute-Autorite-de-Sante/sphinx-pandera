import pandera.pandas as pa
from pandera import Column, Index

basic_schema = pa.DataFrameSchema(
    {
        "field1": Column(
            int, title="Field 1 Title", description="My field description"
        ),
    },
    index=Index(int),
    strict=True,
    coerce=True,
    description="First data model for testing purposes",
)
