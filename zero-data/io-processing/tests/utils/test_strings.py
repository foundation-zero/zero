from io_processing.utils.strings import snake_case


def test_snake_case():
    assert snake_case("CamelCase") == "camel_case"
