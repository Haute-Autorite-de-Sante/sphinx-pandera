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
            ],
        ),
    ],
)
def test_model(documenter, object_path, expected_rst, autodocument):
    actual = autodocument(
        documenter=documenter,
        object_path=object_path,
        testroot="basic",
    )

    assert actual == expected_rst
