from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from zero_modbus_bridge.bridge import ModbusBridge
from zmqtt import MQTTDisconnectedError, MQTTPublishError, MQTTTimeoutError

from zero_hull_temperature.bridge_relay import RelaySwitchingBridge


def _bridge(publish_error: Exception) -> RelaySwitchingBridge:
    broker = MagicMock()
    broker.publish = AsyncMock(side_effect=publish_error)
    return RelaySwitchingBridge(MagicMock(), MagicMock(), broker, [], buffer_size=30)


@pytest.mark.parametrize(
    "error",
    [
        MQTTPublishError(0x83, "Implementation specific error", None),
        MQTTDisconnectedError(),
        MQTTTimeoutError(),
    ],
)
async def test_transient_relay_publish_error_still_runs_modbus_bridge(error):
    bridge = _bridge(error)
    with patch.object(ModbusBridge, "run_once", new_callable=AsyncMock) as run_once:
        await bridge.run_once()
    run_once.assert_awaited_once()


async def test_non_transient_relay_publish_error_propagates():
    bridge = _bridge(ValueError("bad config"))
    with patch.object(ModbusBridge, "run_once", new_callable=AsyncMock) as run_once:
        with pytest.raises(ValueError, match="bad config"):
            await bridge.run_once()
    run_once.assert_not_awaited()
