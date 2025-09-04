import pandas as pd
from pandera.engines import pandas_engine
from pandera.pandas import Check, Column, DataFrameSchema, Index, dtypes
from pandera.typing import Series


# pylint: disable=too-many-lines
@pandas_engine.Engine.register_dtype(
    equivalents=["boolean", pd.BooleanDtype, pd.BooleanDtype()],
)
@dtypes.immutable  # step 2
class LiteralBool(pandas_engine.BOOL):
    def coerce(  # pylint: disable=arguments-renamed
        self, series: pd.Series
    ) -> pd.Series:
        """Coerce a pandas.Series to boolean types."""
        if pd.api.types.is_string_dtype(series):
            series = series.replace({"True": 1, "False": 0})
        return series.astype("boolean")


def check_num_finess_format(num_finess_et: Series[str]) -> Series[bool]:
    """
    Finess identifiers are 9 characters wide (alphanumerical)
    """
    return num_finess_et.str.match("^\\w{9}$")


def check_dataframe_coherence(data_df):
    """
    Dummy check to test dataframe wide checks, defined at the Schema level
    """
    return data_df.notna(axis=1).any()


Evaluations = DataFrameSchema(
    columns={
        "num_finess_et": Column(
            dtype="string",
            checks=[Check(check_num_finess_format)],
            drop_invalid_rows=False,  # Contre-intuitif : Les lignes invalides seront supprimées # Arrivé 1 fois : GRI-xxxxxx
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description="Geographic FINESS Identifier (ex: 920000650)",
            title="Geographic FINESS Identifier",
        ),
        "eval_code": Column(
            dtype="string",
            checks=Check.str_matches(r"^EVAL\-[\d]{1,6}"),
            drop_invalid_rows=False,  # Contre-intuitif : Les lignes invalides seront supprimées # Arrivé 1 fois : GRI-xxxxxx
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "eval_titre": Column(
            dtype="string",
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "eval_statut_code": Column(
            dtype=pd.CategoricalDtype(categories=["Resolved-Completed"]),
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "eval_statut_label": Column(
            dtype=pd.CategoricalDtype(categories=["Clôturée"]),
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "eval_date_debut": Column(
            dtype=pandas_engine.DateTime(  # type: ignore[call-arg]  # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
                to_datetime_kwargs={"format": "%Y%m%d"}
            ),
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "eval_date_fin": Column(
            dtype=pandas_engine.DateTime(  # type: ignore[call-arg] # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
                to_datetime_kwargs={"format": "%Y%m%d"}
            ),
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "eval_date_cloture_tech": Column(
            dtype=pandas_engine.DateTime(  # type: ignore[call-arg] # pylint: disable=no-value-for-parameter,unexpected-keyword-arg
                to_datetime_kwargs={"format": "%Y%m%dT%H%M%S.%f GMT"}
            ),
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "etablissement": Column(
            dtype="string",
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=False,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "mission_code": Column(
            dtype="string",
            checks=Check.str_matches(r"^MISSION\-[\d]{2,6}"),
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=False,
            unique=False,
            coerce=False,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
        "oe_code": Column(
            dtype="string",
            checks=None,
            drop_invalid_rows=True,  # Contre-intuitif : Les lignes invalides soulèveront une erreur
            nullable=True,
            unique=False,
            coerce=True,
            required=True,
            regex=False,
            description=None,
            title=None,
        ),
    },
    checks=[check_dataframe_coherence],
    drop_invalid_rows=True,
    index=Index(
        dtype="int64",
        checks=None,
        nullable=False,
        coerce=False,
        name=None,
        description=None,
        title=None,
    ),
    dtype=None,
    coerce=True,
    strict=False,
    name=None,
    ordered=False,
    unique=None,
    report_duplicates="all",
    unique_column_names=False,
    add_missing_columns=False,
    title=None,
    description=None,
)
