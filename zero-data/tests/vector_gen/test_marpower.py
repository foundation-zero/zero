from zero_data.io_list.managed_topics import ComponentType
from zero_data.vector_gen.marpower import COMPONENT_TYPE_TABLE


def test_every_component_type_has_a_table():
    assert set(COMPONENT_TYPE_TABLE) == set(ComponentType)
