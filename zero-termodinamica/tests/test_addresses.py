from zero_termodinamica.addresses import MODBUS_UNITS


def test_addresses():
    total_adresses = sum(
        len(topic.fields) for unit in MODBUS_UNITS for topic in unit.topics
    )
    assert total_adresses == 262
