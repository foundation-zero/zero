from contextlib import asynccontextmanager
from unittest.mock import Mock

from aiohttp import ClientSession

from zero_prop_test.io_link import Client, DeviceStatus, IoLinkDevice, Pn7515, Sm6120


def test_sm6120():
    raw = bytes.fromhex("00000000FACEFD000BF6FE00")
    result = Sm6120.parse(raw)
    assert result.device_status == DeviceStatus.OK


def test_pn7515():
    raw = bytes.fromhex("00640000")
    result = Pn7515.parse(raw)
    assert result.device_status == DeviceStatus.OK


async def test_client():
    mock = Mock(spec=ClientSession)
    client = Client(mock)
    device = IoLinkDevice("test-device", "yard-tag", "192.168.1.2", 1, Sm6120)

    @asynccontextmanager
    async def mock_response():
        class MockResponse:
            async def json(self):
                return {"data": {"value": "00000000FACEFD000BF6FE00"}}

        yield MockResponse()

    mock.get.return_value = mock_response()
    result = await client.query(device)
    assert result.device_status == DeviceStatus.OK
    mock.get.assert_called_once_with(
        f"http://192.168.1.2/iolinkmaster/port[{device.port}]/iolinkdevice/pdin/getdata"
    )
