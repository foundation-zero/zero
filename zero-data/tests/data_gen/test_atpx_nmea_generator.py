from unittest.mock import AsyncMock, MagicMock

from zero_data.data_gen import AtpxNmeaGenerator
from zero_data.data_gen.atpx_nmea_generator import _CORPUS, _checksum, _sentence


def test_checksum_matches_known_sentence():
    # `$HEROT,000.1,A*2A` is a real captured sentence.
    assert _checksum("HEROT,000.1,A") == "2A"
    assert _sentence("HEROT,000.1,A") == "$HEROT,000.1,A*2A"


async def test_send_messages_publishes_valid_sentence_per_corpus_entry():
    mock_client = AsyncMock()

    gen = AtpxNmeaGenerator(interval=10, mqtt_config=MagicMock())

    await gen.send_messages(mock_client)

    calls = [
        (call.args[0], call.args[1]) for call in mock_client.publish.call_args_list
    ]

    # Exactly one message per corpus entry, each on its sender/type topic.
    assert len(calls) == len(_CORPUS)
    expected_topics = {
        f"atpx/nmea0183/{spec.sender}/{spec.sentence_type}" for spec in _CORPUS
    }
    assert {topic for topic, _payload in calls} == expected_topics

    for _topic, payload in calls:
        assert isinstance(payload, str)
        assert payload.startswith("$")
        body, _, checksum = payload[1:].partition("*")
        assert checksum == _checksum(body)


def test_topic_type_matches_sentence_formatter():
    # <TYPE> becomes the greptime table name, so it must be the sentence's
    # formatter, not an arbitrary label.
    for spec in _CORPUS:
        address = spec.body().split(",", 1)[0]
        # Proprietary sentences ($P<manufacturer>) drop the manufacturer:
        # PFEC -> FEC.
        if address.startswith("P"):
            assert address.endswith(spec.sentence_type)
        else:
            assert address[-3:] == spec.sentence_type
