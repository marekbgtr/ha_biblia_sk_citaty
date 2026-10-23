"""Daily selection with persistent cache and explicit stale-data status."""
from datetime import timedelta
import hashlib
import logging
from aiohttp import ClientError
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.util import dt as dt_util
from .api import async_fetch
from .const import CONF_PASSAGES, DEFAULT_PASSAGES, DOMAIN, TRANSLATION
from .parser import parse_passages

_LOGGER = logging.getLogger(__name__)

class BibliaCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, _LOGGER, name=DOMAIN, update_interval=timedelta(minutes=15))
        raw = entry.options.get(CONF_PASSAGES, entry.data.get(CONF_PASSAGES, DEFAULT_PASSAGES))
        self.passages = parse_passages(raw)
        self.signature = hashlib.sha256(raw.encode()).hexdigest()
        self.store = Store(hass, 1, f'{DOMAIN}.{entry.entry_id}')
        self.cached = None
        self.session = async_get_clientsession(hass)
        self.failed = False

    async def async_load_cache(self):
        cached = await self.store.async_load()
        if (isinstance(cached, dict) and cached.get('signature') == self.signature
                and all(isinstance(cached.get(k), str) and cached[k]
                        for k in ('text', 'odkaz', 'datum', 'url', 'preklad'))):
            self.cached = cached

    async def _async_update_data(self):
        today = dt_util.now().date()
        date_string = today.isoformat()
        if self.cached and self.cached['datum'] == date_string:
            return {**self.cached, 'aktualne': True}
        passage = self.passages[today.toordinal() % len(self.passages)]
        try:
            text = await async_fetch(self.hass, self.session, passage)
        except (ClientError, TimeoutError, ValueError) as err:
            if not self.cached:
                raise UpdateFailed(f'Cannot load Biblia.sk: {err}') from err
            if not self.failed:
                _LOGGER.warning('Biblia.sk unavailable; displaying cached passage: %s', err)
                self.failed = True
            return {**self.cached, 'aktualne': False}
        if self.failed:
            _LOGGER.info('Biblia.sk connection restored')
        self.failed = False
        self.cached = {'signature': self.signature, 'odkaz': passage.reference,
                       'text': text, 'url': passage.url, 'preklad': TRANSLATION,
                       'datum': date_string, 'aktualne': True}
        try:
            await self.store.async_save(self.cached)
        except OSError:
            _LOGGER.exception('Cannot persist Biblia.sk cache')
        return dict(self.cached)
