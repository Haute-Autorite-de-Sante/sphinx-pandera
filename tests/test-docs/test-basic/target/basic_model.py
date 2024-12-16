import pandera as pa


class TestModel(pa.DataFrameModel):
    """
    First data model for testing purposes
    """

    field1: int = pa.Field(
        title="Field 1 Title",
        description="My field description",
    )
