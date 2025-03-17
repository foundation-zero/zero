from simulation.collector import Collector


def test_empty():
    col = Collector()
    assert col.result() is None


def test_single():
    col = Collector()
    col.collect({"a": 1.0})
    result = col.result()
    assert result is not None
    assert result["a"].to_list() == [1.0]


def test_multiple():
    col = Collector()
    for i in range(200):
        col.collect({"a": float(i)})
    result = col.result()
    assert result is not None
    assert result["a"].len() == 200
