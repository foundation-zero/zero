from zero_data.io_list.extra_topics import EXTRA_TOPICS
from zero_data.io_list.managed_topics import ComponentType
from zero_data.vector_gen.marpower import COMPONENT_TYPE_TABLE


def test_every_managed_component_type_has_a_table():
    spec_only = {topic.component for topic in EXTRA_TOPICS}

    assert set(COMPONENT_TYPE_TABLE) == set(ComponentType) - spec_only
