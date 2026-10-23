import asyncio, tempfile, os, inspect
from pathlib import Path
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntries
from homeassistant import loader
from homeassistant.helpers import entity_registry, device_registry, area_registry

async def main():
 with tempfile.TemporaryDirectory() as tmp:
  os.symlink(Path(__file__).resolve().parents[1] / 'custom_components',Path(tmp)/'custom_components')
  hass=HomeAssistant(tmp)
  loader.async_setup(hass)
  hass.config_entries=ConfigEntries(hass,{})
  await hass.config_entries.async_initialize()
  await entity_registry.async_load(hass)
  await device_registry.async_load(hass)
  await area_registry.async_load(hass)
  with patch('custom_components.biblia_sk.config_flow.async_get_clientsession',return_value=object()),patch('custom_components.biblia_sk.coordinator.async_get_clientsession',return_value=object()),patch('custom_components.biblia_sk.config_flow.async_fetch',new=AsyncMock(return_value='Example')),patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(return_value='Example')):
   result=await hass.config_entries.flow.async_init('biblia_sk',context={'source':'user'})
   assert result['type']=='form',result
   result=await hass.config_entries.flow.async_configure(result['flow_id'],{'passages':'mk 1:14-15'})
   assert result['type']=='create_entry',result
   await hass.async_block_till_done()
   state=hass.states.get('sensor.biblicky_citat')
   assert state and state.attributes['text']=='Example',state
   entry=result['result']
   options=await hass.config_entries.options.async_init(entry.entry_id)
   assert options['type']=='form',options
   options=await hass.config_entries.options.async_configure(options['flow_id'],{'passages':'mt 11:28-30'})
   assert options['type']=='create_entry',options
   await hass.async_block_till_done()
   assert hass.states.get('sensor.biblicky_citat').state=='Mt 11,28–30'
   await hass.config_entries.async_unload(entry.entry_id)
   assert entry.entry_id not in hass.data['biblia_sk']
   print('SMOKE OK: UI setup, sensor creation, options update/reload, unload')
  await hass.async_stop()
asyncio.run(main())
