from loads.util import camel_to_kebab, camel_to_title, hyphenize, snake_to_title


def test_hyphenize():
    assert hyphenize("this_is_a_test") == "this-is-a-test"


def test_camel_to_kebab():
    assert camel_to_kebab("ThisIsATest") == "this-is-a-test"


def test_camel_to_title():
    assert camel_to_title("ThisIsATest") == "This Is A Test"


def test_snake_to_title():
    assert snake_to_title("a_b") == "A B"
