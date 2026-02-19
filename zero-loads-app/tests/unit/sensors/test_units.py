from loads.sensors.units import VariableMeta


def test_variable_meta_override():
    meta1 = VariableMeta(name="test", display_name="Test", scale_min=0, scale_max=100)
    meta2 = VariableMeta(name="test", display_name="Test Override", scale_max=10)

    overridden_meta = meta1.override(meta2)

    assert overridden_meta.name == "test"
    assert overridden_meta.display_name == "Test Override"
    assert overridden_meta.scale_min == 0
    assert overridden_meta.scale_max == 10
