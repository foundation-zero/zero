from unittest.mock import MagicMock, patch

from zero_prop_test.settings import Settings
from zero_prop_test.twincat import Client, Variable as TwincatVariable


def test_query_reads_variable_by_name():
    plc = MagicMock()
    plc.read_by_name.return_value = 123
    client = Client(plc)

    result = client.query(TwincatVariable(name="GVL.test", type="INT"))

    assert result == 123
    plc.read_by_name.assert_called_once_with("GVL.test")


def test_from_settings_creates_and_opens_connection():
    settings = Settings(
        iolink_host="127.0.0.1",
        iolink_port=1,
        modbus_host="127.0.0.1",
        modbus_port=2,
        twincat_self_netid="1.2.3.4.5.6",
        twincat_ip="192.168.0.10",
        twincat_netid="5.6.7.8.9.10",
        twincat_port=852,
        twincat_username="user",
        twincat_password="password",
        twincat_route_name="route",
        twincat_prefices=[
            "ThrusterTest.",
            "CanAradex.",
            "CanAkasol.act_P_BatteryPower_kW",
        ],
        mqtt_host="127.0.0.1",
        mqtt_port=3,
        mqtt_username="mqtt-user",
        mqtt_password="mqtt-password",
    )
    plc = MagicMock()
    plc.get_local_address.return_value = "1.2.3.4.5.6"

    with patch("zero_prop_test.twincat.set_local_address") as set_local_address:
        with patch("zero_prop_test.twincat.Connection", return_value=plc) as connection:
            with Client.from_settings(settings) as client:
                assert isinstance(client, Client)
                assert client._plc is plc

    set_local_address.assert_called_once_with(settings.twincat_self_netid)
    connection.assert_called_once_with(
        settings.twincat_netid,
        settings.twincat_port,
        settings.twincat_ip,
    )
    plc.__enter__.assert_called_once_with()
    plc.__exit__.assert_called_once()
