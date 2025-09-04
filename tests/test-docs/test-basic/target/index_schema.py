import pandera.pandas as pa

single_index_schema = pa.DataFrameSchema(
    index=pa.Index(
        str,
        unique=True,
        checks=[
            pa.Check.str_matches(r"^AIPE-[0-9]+$"),
        ],
        name="key",
        title="First Index type field",
        description="Field whose dtype is Index",
    ),
    strict=True,
    coerce=True,
    description="Schema with a single field which is a pandas index",
)


multi_index_schema = pa.DataFrameSchema(
    index=pa.MultiIndex(
        [
            pa.Index(
                str,
                unique=True,
                checks=[
                    pa.Check.str_matches(r"^AIPE-[0-9]+$"),
                ],
                name="key1",
                title="First Index type field",
                description="Field whose dtype is Index",
            ),
            pa.Index(
                str,
                unique=True,
                checks=[
                    pa.Check.str_matches(r"^AIPE2-[0-9]+$"),
                ],
                name="key2",
                title="Second Index type field",
                description="Field whose dtype is Index",
            ),
        ]
    ),
    strict=True,
    coerce=True,
    description="Schema with two fields which are a pandas index (multiIndex)",
)
