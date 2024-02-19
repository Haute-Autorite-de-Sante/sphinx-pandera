def test_model_basic(autodocument):
    actual = autodocument(
        documenter="pandera_model",
        object_path="target.basic_model.TestModel",
        testroot="basic",
    )

    assert actual == [
        "",
        ".. py:pandera_model:: TestModel",
        "   :module: target.basic_model",
        "",
        "   First data model for testing purposes",
        "",
    ]
