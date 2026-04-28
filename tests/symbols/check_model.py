import pandas as pd
import pandera.pandas as pa
from pandera.engines.pandas_engine import DateTime
from pandera.typing import Series

# pylint: disable-next=unexpected-keyword-arg,no-value-for-parameter
Date: DateTime = DateTime(unit="D", to_datetime_kwargs={"format": "%Y-%m-%d"})  # type: ignore


class TestModel(pa.DataFrameModel):
    """
    Data model with checks
    """

    # pylint: disable=too-few-public-methods,no-self-argument
    class Config:
        strict = True
        coerce = True

    date_export: Series[Date] = pa.Field(  # type: ignore
        title="Export date",
        description=(
            "Date of the export, exports are made available on a yearly basis"
        ),
        coerce=True,
    )
    num_finess_et: Series[str] = pa.Field(
        title="Geographic FINESS Identifier",
        description="Geographic FINESS Identifier (ex: 920000650)",
    )
    num_finess_ej: Series[str] = pa.Field(
        title="Juridic FINESS Identifier",
        description="Identifider of the juridic entity (ex: 920150059)",
    )

    latitude: Series[float] = pa.Field(
        title="Latitude",
        description=(
            "Latitude of the location of the care center"
            "(WGS 84) (ex: 48.84512493935407)"
        ),
        nullable=True,
        le=90,
        ge=-90,
    )
    longitude: Series[float] = pa.Field(
        title="Longitude",
        description=(
            "Longitude of the location of the care center"
            "(WGS 84) (ex: 48.84512493935407)"
        ),
        nullable=True,
        le=180,
        ge=-180,
    )

    @pa.check("num_finess_e.", regex=True, name="check_num_finess_format")
    def check_num_finess_format(
        cls, num_finess_et: Series[str]
    ) -> Series[bool]:
        """
        Finess identifiers are 9 characters wide (alphanumerical)
        """
        return num_finess_et.str.match("^\\w{9}$")

    @pa.dataframe_check
    def check_coords_non_null(cls, data_df: pd.DataFrame) -> Series[bool]:
        """
        Longitude and latitude should not be null starting 2017
        """
        return (
            (data_df["date_export"].dt.year > 2017)
            & data_df["latitude"].notna()
            & data_df["longitude"].notna()
        ) | (data_df["date_export"].dt.year <= 2017)
