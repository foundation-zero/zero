from zero_termodinamica.io import read_modbus_topics


def test_io():
    topics = read_modbus_topics()
    # 31 AC rooms + 1 ac-misc = 32 topics
    assert len(topics) == 32
