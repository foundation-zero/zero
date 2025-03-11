"""The rena integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ADDRESS, CONF_ID, Platform
from homeassistant.core import HomeAssistant
import voluptuous as vol
# from .const import DOMAIN, CONF_B2P_HOST, CONF_B2P_PDC, CONF_B2P_GROUPS

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
# PLATFORMS: list[Platform] = [Platform.LIGHT]

# # TODO Create ConfigEntry type alias with API object
# # TODO Rename type alias and update all entry annotations
# type B2pConfigEntry = ConfigEntry[RenaAPI]  # noqa: F821

# # CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.All(vol.Schema({
# #     vol.Optional(str(Platform.LIGHT)): vol.Schema({
# #         vol.Required(CONF_B2P_HOST): str,
# #         vol.Required(CONF_B2P_PDC): int,
# #         vol.Required(CONF_B2P_GROUPS): vol.All(int)
# #     })
# # }))})


# class RenaAPI:
#     def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
#         self.host = entry.data[CONF_ADDRESS]
#         self.pdc = entry.data[CONF_ID]


# async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
#     hass.config_entries
#     return True

# # TODO Update entry annotation
# async def async_setup_entry(hass: HomeAssistant, entry: B2pConfigEntry) -> bool:
#     """Set up rena from a config entry."""

#     # TODO 1. Create API instance
#     # TODO 2. Validate the API connection (and authentication)
#     # TODO 3. Store an API object for your platforms to access
#     # entry.runtime_data = MyAPI(...)

#     await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

#     return True


# # TODO Update entry annotation
# async def async_unload_entry(hass: HomeAssistant, entry: B2pConfigEntry) -> bool:
#     """Unload a config entry."""
#     return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
