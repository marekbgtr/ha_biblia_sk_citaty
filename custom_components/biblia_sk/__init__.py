"""Unofficial Biblia.sk integration."""
from homeassistant.const import Platform
from .const import DOMAIN
from .coordinator import BibliaCoordinator

PLATFORMS = [Platform.SENSOR]

async def async_setup_entry(hass, entry):
    coordinator = BibliaCoordinator(hass, entry)
    await coordinator.async_load_cache()
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_update_options))
    return True

async def async_update_options(hass, entry):
    await hass.config_entries.async_reload(entry.entry_id)

async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)
        return True
    return False

async def async_remove_entry(hass, entry):
    from homeassistant.helpers.storage import Store
    await Store(hass, 1, f'{DOMAIN}.{entry.entry_id}').async_remove()
