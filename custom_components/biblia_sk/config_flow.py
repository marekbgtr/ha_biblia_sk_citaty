"""Set up and change the reference list from the Home Assistant UI."""
import voluptuous as vol
from aiohttp import ClientError
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.selector import TextSelector, TextSelectorConfig
from .api import async_fetch
from .const import DOMAIN, NAME, CONF_PASSAGES, DEFAULT_PASSAGES
from .parser import parse_passages


def schema(default):
    return vol.Schema({vol.Required(CONF_PASSAGES, default=default): TextSelector(TextSelectorConfig(multiline=True))})

async def validate(hass, user_input):
    try:
        passages = parse_passages(user_input[CONF_PASSAGES])
    except ValueError:
        return {'base': 'invalid_passages'}
    try:
        await async_fetch(hass, async_get_clientsession(hass), passages[0])
    except (ClientError, TimeoutError):
        return {'base': 'cannot_connect'}
    except ValueError:
        return {'base': 'missing_verses'}
    return {}

class BibliaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()
        errors = {}
        if user_input is not None:
            errors = await validate(self.hass, user_input)
            if not errors:
                return self.async_create_entry(title=NAME, data=user_input)
        default = user_input[CONF_PASSAGES] if user_input else DEFAULT_PASSAGES
        return self.async_show_form(step_id='user', data_schema=schema(default), errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return BibliaOptionsFlow()

class BibliaOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input=None):
        errors = {}
        if user_input is not None:
            errors = await validate(self.hass, user_input)
            if not errors:
                return self.async_create_entry(title='', data=user_input)
        default = self.config_entry.options.get(CONF_PASSAGES, self.config_entry.data.get(CONF_PASSAGES, DEFAULT_PASSAGES))
        if user_input:
            default = user_input[CONF_PASSAGES]
        return self.async_show_form(step_id='init', data_schema=schema(default), errors=errors)
