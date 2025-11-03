from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ColorMode,
    LightEntity,
    LightEntityDescription,
    PLATFORM_SCHEMA_BASE,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import socket
import voluptuous as vol
from .const import DOMAIN, CONF_B2P_HOST, CONF_B2P_PDC, CONF_B2P_CHANNEL, DATA_SOCKET

PLATFORM_SCHEMA = PLATFORM_SCHEMA_BASE.extend(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_B2P_HOST): str,
        vol.Required(CONF_B2P_PDC): int,
        vol.Required(CONF_B2P_CHANNEL): int,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    sock = hass.data.get(DATA_SOCKET, socket.socket(socket.AF_INET, socket.SOCK_DGRAM))
    add_entities(
        [
            RenaLight(
                config[CONF_NAME],
                config[CONF_B2P_HOST],
                config[CONF_B2P_PDC],
                config[CONF_B2P_CHANNEL],
                sock,
            )
        ]
    )


class RenaLight(LightEntity):
    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}
    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, name: str, host: str, pdc: int, channel: int, sock):
        self._is_on = False
        self._brightness = 0
        self._attr_name = name
        self._attr_unique_id = f"{host}_{pdc}_{channel}"
        self._host = host
        self._pdc = pdc
        self._channel = channel
        self._sock = sock

    @property
    def is_on(self):
        """If the switch is currently on or off."""
        return self._is_on

    @property
    def brightness(self):
        return self._brightness

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._is_on = True
        fade_time_ms = 100
        self._brightness = kwargs.get(ATTR_BRIGHTNESS, 255)

        self._sock.sendto(
            bytes(
                f"@FADE( {self._pdc}, {fade_time_ms} ) SOLL {{ {self._channel}={int(self._brightness / 2.55)} }}\n",
                "ascii",
            ),
            (self._host, 50000),
        )

    def turn_off(self, **kwargs):
        """Turn the switch off."""
        self._is_on = False
