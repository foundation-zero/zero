from zero_termodinamica.addresses import read_modbus_units


def test_addresses():
    total_adresses = sum(
        len(topic.fields) for unit in read_modbus_units() for topic in unit.topics
    )
    assert total_adresses == 262
