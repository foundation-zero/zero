from unittest.mock import AsyncMock, MagicMock

from zero_data.data_gen import AtpxGenerator
from zero_data.data_gen.atpx_generator import _SOURCES


async def test_send_messages_publishes_every_field_and_source():
    all_field_ids = [4864, 4866, 1025]
    mock_client = AsyncMock()

    gen = AtpxGenerator(
        interval=10,
        mqtt_config=MagicMock(),
        field_ids=all_field_ids,
    )

    await gen.send_messages(mock_client)

    calls = [
        (call.args[0], call.args[1]) for call in mock_client.publish.call_args_list
    ]

    expected_topics = {
        f"atpx/{field_id}/{source}" for field_id in all_field_ids for source in _SOURCES
    }

    # Exactly one message per (field, source) pair.
    assert len(calls) == len(all_field_ids) * len(_SOURCES)

    actual_topics = [topic for topic, _payload in calls]
    assert set(actual_topics) == expected_topics
    # No duplicate topics either.
    assert len(actual_topics) == len(set(actual_topics))

    for _topic, payload in calls:
        assert isinstance(payload, str)
        assert "{" not in payload
        assert '"' not in payload
        float(payload)  # parses without error


def test_serialize_message_returns_bare_number_string():
    gen = AtpxGenerator(
        interval=MagicMock(),
        mqtt_config=MagicMock(),
        field_ids=[],
    )

    payload = gen.serialize_message(12.3)

    assert payload == "12.3"
    assert float(payload) == 12.3
    assert "{" not in payload
    assert '"' not in payload
