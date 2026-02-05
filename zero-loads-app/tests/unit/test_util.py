from loads.util import camel_to_kebab, hyphenize


def test_hyphenize():
    assert hyphenize("this_is_a_test") == "this-is-a-test"


def test_camel_to_kebab():
    assert camel_to_kebab("ThisIsATest") == "this-is-a-test"
