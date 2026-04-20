from unittest.mock import MagicMock

from domestic_control.app import LogDataLoader, app, data_collection, log_data_loader
from domestic_control.mqtt import DataCollection
from pytest import fixture


@fixture
def test_app():
    app.dependency_overrides[data_collection] = lambda: MagicMock(spec=DataCollection)
    app.dependency_overrides[log_data_loader] = lambda: MagicMock(spec=LogDataLoader)
    return app
