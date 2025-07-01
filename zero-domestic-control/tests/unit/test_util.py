from zero_domestic_control.util import invert_dict


def test_invert_dict_empty():
    assert invert_dict({}) == {}


def test_invert_dict():
    assert invert_dict({"a": 1, "b": 2}) == {1: "a", 2: "b"}
