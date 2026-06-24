from zero_termodinamica.io import read_modbus_units


def test_io():
    total_adresses = sum(
        len(topic.fields) for unit in read_modbus_units() for topic in unit.topics
    )
    assert total_adresses == 262
