from datetime import datetime
from orchestration.collector import PolarsCollector


def test_empty():
    col = PolarsCollector()
    assert col.result() is None


def test_single():
    col = PolarsCollector()
    col.collect({"a": 1.0}, datetime(2021, 1, 1))
    result = col.result()
    assert result is not None
    assert result["a"].to_list() == [1.0]
    assert result["time"].to_list() == [datetime(2021, 1, 1)]


def test_multiple():
    col = PolarsCollector()
    for i in range(200):
        col.collect({"a": float(i)}, datetime.now())
    result = col.result()
    assert result is not None
    assert result["a"].len() == 200
