import pandera.pandas as pa

basic_schema = pa.DataFrameSchema(
    {
        "field1": pa.Column(
            int, title="Field 1 Title", description="My field description"
        ),
    },
    index=pa.Index(int),
    strict=True,
    coerce=True,
    description="First data model for testing purposes",
)
