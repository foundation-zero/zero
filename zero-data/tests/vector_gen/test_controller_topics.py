from zero_data.io_list.managed_topics import ComponentType
from zero_data.vector_gen.controller_topics import generate_controller_managed_topics


def test_every_controlled_module_stores_its_automation_mode():
    automation_mode_topics = {
        topic.topic.topic
        for topic in generate_controller_managed_topics()
        if topic.component == ComponentType.AUTOMATION_MODE
    }

    assert automation_mode_topics == {
        f"thrs/controller/{module}/automation-mode"
        for module in (
            "adsorption",
            "consumers",
            "dc",
            "dhw",
            "drives",
            "pcm",
            "pvt",
            "thrusters",
        )
    }
