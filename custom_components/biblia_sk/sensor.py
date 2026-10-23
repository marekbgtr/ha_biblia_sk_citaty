"""Passage sensor; long text lives in attributes, not the state."""
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN

PARALLEL_UPDATES = 0

async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([BibliaSensor(hass.data[DOMAIN][entry.entry_id], entry)])

class BibliaSensor(CoordinatorEntity, SensorEntity):
    _attr_name = 'Biblický citát'
    _attr_icon = 'mdi:book-open-page-variant'
    _attr_attribution = 'Zdroj: Biblia.sk; Jeruzalemská Biblia – Botek'

    def __init__(self, coordinator, entry):
        super().__init__(coordinator)
        self._attr_unique_id = f'{entry.entry_id}_passage'

    @property
    def native_value(self):
        return self.coordinator.data['odkaz']

    @property
    def extra_state_attributes(self):
        return {k: self.coordinator.data[k] for k in
                ('text', 'preklad', 'url', 'datum', 'aktualne')}
