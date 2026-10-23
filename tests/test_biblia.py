"""Run with python -m unittest discover -s tests -v (Home Assistant installed)."""
from datetime import datetime
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import AsyncMock, patch
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
from custom_components.biblia_sk.parser import parse_passages, extract_text
from custom_components.biblia_sk.coordinator import BibliaCoordinator
from custom_components.biblia_sk.sensor import BibliaSensor
from custom_components.biblia_sk.config_flow import validate
from homeassistant.helpers.update_coordinator import UpdateFailed

class ParserTests(unittest.TestCase):
    def test_inline_markup_entities_and_numbers(self):
        p = parse_passages('mk 1:14-15')[0]
        html = '<h2>Heading</h2><span data-verse="14" data-chapter="1"><span><sup>14</sup></span><span>Hello <b>world</b> &amp; all.</span></span><span data-verse="15" data-chapter="1"><sup>15</sup>Next<br/>line.</span><script>noise</script>'
        self.assertEqual(extract_text(html,p),'Hello world & all.\n\nNext line.')
    def test_missing_verse(self):
        with self.assertRaises(ValueError): extract_text('',parse_passages('mk 1:1')[0])
    def test_invalid_inputs(self):
        for value in ['', 'https://evil.example 1:1', '../mk 1:1', 'mk 0:1', 'mk 1:5-2', 'mk 1:1-100']:
            with self.subTest(value=value), self.assertRaises(ValueError): parse_passages(value)
    def test_reference(self):
        self.assertEqual(parse_passages('1kor 13:4-7')[0].reference,'1 Kor 13,4–7')
        self.assertEqual(parse_passages('mk 1:15')[0].reference,'Mk 1,15')

class CoordinatorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.hass = HomeAssistant(self.directory.name)
        self.entry = SimpleNamespace(entry_id='test',options={},data={})
        with patch('custom_components.biblia_sk.coordinator.async_get_clientsession',return_value=object()):
            self.c = BibliaCoordinator(self.hass,self.entry)
        self.c.store = SimpleNamespace(async_save=AsyncMock(),async_load=AsyncMock(return_value=None))
    async def asyncTearDown(self):
        await self.hass.async_stop()
        self.directory.cleanup()
    async def test_daily_cache_no_second_http_call(self):
        with patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(return_value='Example')) as fetch:
            first = await self.c._async_update_data()
            self.assertEqual(first,await self.c._async_update_data())
            fetch.assert_awaited_once()
            self.c.store.async_save.assert_awaited_once()
    async def test_failed_first_fetch_is_not_ready(self):
        with patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(side_effect=TimeoutError)):
            with self.assertRaises(UpdateFailed): await self.c._async_update_data()
    async def test_old_cache_then_recovery(self):
        old={'signature':self.c.signature,'text':'Old','odkaz':'Mk 1,15','preklad':'Botek','url':'https://biblia.sk','datum':'2000-01-01','aktualne':True}
        self.c.store.async_load.return_value = old
        await self.c.async_load_cache()
        with patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(side_effect=TimeoutError)):
            data=await self.c._async_update_data()
            self.assertFalse(data['aktualne']); self.assertEqual(data['text'],'Old')
        with patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(return_value='New')):
            data=await self.c._async_update_data()
            self.assertTrue(data['aktualne']); self.assertEqual(data['text'],'New')
    async def test_changed_options_invalidate_cache(self):
        self.c.store.async_load.return_value={'signature':'different','text':'old'}
        await self.c.async_load_cache()
        self.assertIsNone(self.c.cached)
    async def test_day_rollover(self):
        with patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(return_value='Example')) as fetch:
            with patch('custom_components.biblia_sk.coordinator.dt_util.now',return_value=datetime(2026,10,23,23,59)):
                first=await self.c._async_update_data()
            with patch('custom_components.biblia_sk.coordinator.dt_util.now',return_value=datetime(2026,10,24,0,1)):
                second=await self.c._async_update_data()
            self.assertNotEqual(first['odkaz'],second['odkaz']); self.assertEqual(fetch.await_count,2)
    async def test_sensor_long_text_kept_in_attributes(self):
        with patch('custom_components.biblia_sk.coordinator.async_fetch',new=AsyncMock(return_value='Text '*300)):
            self.c.data=await self.c._async_update_data()
        sensor=BibliaSensor(self.c,self.entry)
        self.assertLess(len(sensor.native_value),256)
        self.assertEqual(len(sensor.extra_state_attributes['text']),1500)
    async def test_invalid_form_does_not_fetch(self):
        with patch('custom_components.biblia_sk.config_flow.async_fetch',new=AsyncMock()) as fetch:
            self.assertEqual(await validate(self.hass,{'passages':'bad'}),{'base':'invalid_passages'})
            fetch.assert_not_awaited()
