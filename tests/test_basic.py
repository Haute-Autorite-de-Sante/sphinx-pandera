import pytest


@pytest.mark.parametrize(
    "documenter,object_path,expected_rst",
    [
        (
            "pandera_model",
            "target.basic_model.TestModel",
            [
                "",
                ".. py:pandera_model:: TestModel",
                "   :module: target.basic_model",
                "",
                "   First data model for testing purposes",
                "",
                "",
                "   .. py:pandera_field:: TestModel.field1",
                "      :module: target.basic_model",
                "      :type: int",
                "      :title: Field 1 Title",
                "",
                "      My field description",
                "",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "",
                "   .. py:pandera_model_config:: TestModel.Config",
                "      :module: target.basic_model",
                "      :canonical: pandera.api.dataframe.model.Config",
                "",
                "",
                "      .. py:attribute:: TestModel.Config.coerce",
                "         :module: target.basic_model",
                "         :type: bool",
                "",
                "         coerce types of all schema components",
                "",
                "",
                "      .. py:attribute:: TestModel.Config.ordered",
                "         :module: target.basic_model",
                "         :type: bool",
                "",
                "         validate columns order",
                "",
                "",
                "      .. py:attribute:: TestModel.Config.strict",
                "         :module: target.basic_model",
                "         :type: StrictType",
                "",
                "         make sure all specified columns are in the validated dataframe -",
                '         if ``"filter"``, removes columns not specified in the schema',
                "",
            ],
        ),
        (
            "pandera_model",
            "target.check_model.TestModel",
            [
                "",
                ".. py:pandera_model:: TestModel",
                "   :module: target.check_model",
                "",
                "   Data model with checks",
                "",
                "",
                "   .. py:pandera_model_config:: TestModel.Config",
                "      :module: target.check_model",
                "",
                "",
                "      .. py:attribute:: TestModel.Config.strict",
                "         :module: target.check_model",
                "         :value: True",
                "",
                "",
                "      .. py:attribute:: TestModel.Config.coerce",
                "         :module: target.check_model",
                "         :value: True",
                "",
                "",
                "   .. py:pandera_field:: TestModel.date_export",
                "      :module: target.check_model",
                "      :type: ~pandera.typing.pandas.Series[DataType(datetime64[ns])]",
                "      :title: Export date",
                "",
                "      Date of the export, exports are made available on a yearly basis",
                "",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: TestModel.num_finess_et",
                "      :module: target.check_model",
                "      :type: ~pandera.typing.pandas.Series[str]",
                "      :title: Geographic FINESS Identifier",
                "",
                "      Geographic FINESS Identifier (ex: 920000650)",
                "",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "      :Validated by:",
                "         - :py:obj:`check_num_finess_format "
                "<target.check_model.TestModel.check_num_finess_format>`",
                "",
                "   .. py:pandera_field:: TestModel.num_finess_ej",
                "      :module: target.check_model",
                "      :type: ~pandera.typing.pandas.Series[str]",
                "      :title: Juridic FINESS Identifier",
                "",
                "      Identifider of the juridic entity (ex: 920150059)",
                "",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "      :Validated by:",
                "         - :py:obj:`check_num_finess_format "
                "<target.check_model.TestModel.check_num_finess_format>`",
                "",
                "   .. py:pandera_field:: TestModel.latitude",
                "      :module: target.check_model",
                "      :type: ~pandera.typing.pandas.Series[float]",
                "      :title: Latitude",
                "",
                "      Latitude of the location of the care center(WGS 84) (ex: "
                "48.84512493935407)",
                "",
                "",
                "      :Constraints:",
                "         - **nullable** = True",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "      :Validated by:",
                "         - **greater_than_or_equal_to(-90)**",
                "         - **less_than_or_equal_to(90)**",
                "",
                "   .. py:pandera_field:: TestModel.longitude",
                "      :module: target.check_model",
                "      :type: ~pandera.typing.pandas.Series[float]",
                "      :title: Longitude",
                "",
                "      Longitude of the location of the care center(WGS 84) (ex: "
                "48.84512493935407)",
                "",
                "",
                "      :Constraints:",
                "         - **nullable** = True",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "      :Validated by:",
                "         - **greater_than_or_equal_to(-180)**",
                "         - **less_than_or_equal_to(180)**",
                "",
                "   .. py:pandera_check:: TestModel.check_num_finess_format(num_finess_et: "
                "~pandera.typing.pandas.Series[str]) -> ~pandera.typing.pandas.Series[bool]",
                "      :module: target.check_model",
                "      :classmethod:",
                "",
                "      Finess identifiers are 9 characters wide (alphanumerical)",
                "",
                "      :Validates:",
                "         - :py:obj:`num_finess_et "
                "<target.check_model.TestModel.num_finess_et>`",
                "         - :py:obj:`num_finess_ej "
                "<target.check_model.TestModel.num_finess_ej>`",
                "",
                "",
                "   .. py:pandera_check:: TestModel.check_coords_non_null(data_df: "
                "~pandas.core.frame.DataFrame) -> ~pandera.typing.pandas.Series[bool]",
                "      :module: target.check_model",
                "      :classmethod:",
                "",
                "      Longitude and latitude should not be null starting 2017",
                "",
            ],
        ),
    ],
)
def test_basic_model(documenter, object_path, expected_rst, autodocument):
    actual = autodocument(
        documenter=documenter,
        object_path=object_path,
        testroot="basic",
    )
    assert actual == expected_rst


@pytest.mark.parametrize(
    "documenter,object_path,expected_rst",
    [
        (
            "pandera_schema",
            "target.basic_schema.basic_schema",
            [
                "",
                ".. py:pandera_schema:: basic_schema",
                "   :module: target.basic_schema",
                "",
                "   First data model for testing purposes",
                "",
                "",
                "   :Schema Configuration:",
                "         - **coerce** = True",
                "         - **ordered** = False",
                "         - **strict** = True",
                "",
                "   .. py:pandera_field:: basic_schema.field1",
                "      :type: int64",
                "      :title: Field 1 Title",
                "",
                "      My field description",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "",
                "",
            ],
        ),
        (
            "pandera_schema",
            "target.check_schema.Evaluations",
            [
                "",
                ".. py:pandera_schema:: Evaluations",
                "   :module: target.check_schema",
                "",
                "   :Schema Configuration:",
                "         - **coerce** = True",
                "         - **ordered** = False",
                "         - **strict** = False",
                "",
                "   .. py:pandera_field:: Evaluations.num_finess_et",
                "      :type: string[python]",
                "      :title: Geographic FINESS Identifier",
                "",
                "      Geographic FINESS Identifier (ex: 920000650)",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "      :Validated by:",
                "         - :py:obj:`check_num_finess_format <target.check_schema.check_num_finess_format>`",
                "",
                "   .. py:pandera_field:: Evaluations.eval_code",
                "      :type: string[python]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "      :Validated by:",
                "         - **str_matches('^EVAL\\-[\\d]{1,6}')**",
                "",
                "   .. py:pandera_field:: Evaluations.eval_titre",
                "      :type: string[python]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.eval_statut_code",
                "      :type: category",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.eval_statut_label",
                "      :type: category",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.eval_date_debut",
                "      :type: datetime64[ns]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.eval_date_fin",
                "      :type: datetime64[ns]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.eval_date_cloture_tech",
                "      :type: datetime64[ns]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.etablissement",
                "      :type: string[python]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "",
                "   .. py:pandera_field:: Evaluations.mission_code",
                "      :type: string[python]",
                "",
                "      :Constraints:",
                "         - **nullable** = False",
                "         - **unique** = False",
                "         - **coerce** = False",
                "         - **required** = True",
                "",
                "      :Validated by:",
                "         - **str_matches('^MISSION\\-[\\d]{2,6}')**",
                "",
                "   .. py:pandera_field:: Evaluations.oe_code",
                "      :type: string[python]",
                "",
                "      :Constraints:",
                "         - **nullable** = True",
                "         - **unique** = False",
                "         - **coerce** = True",
                "         - **required** = True",
                "",
                "   .. py:pandera_check:: check_num_finess_format",
                "",
                "      Finess identifiers are 9 characters wide (alphanumerical)",
                "",
                "      :Validates:",
                "         - :py:obj:`num_finess_et`",
                "",
                "   .. py:pandera_check:: check_dataframe_coherence",
                "",
                "      Dummy check to test dataframe wide checks, defined at the Schema level",
            ],
        ),
    ],
)
def test_basic_schema(documenter, object_path, expected_rst, autodocument):
    actual = autodocument(
        documenter=documenter,
        object_path=object_path,
        testroot="basic",
        options_doc={"no-value": ""},  # Disable value doc
    )
    assert actual == expected_rst
