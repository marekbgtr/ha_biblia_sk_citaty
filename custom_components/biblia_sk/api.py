"""Asynchronous HTTP access to the public chapter pages."""
import asyncio
from .parser import extract_text

async def async_fetch(hass, session, passage):
    async with asyncio.timeout(25):
        async with session.get(passage.url, headers={'User-Agent': 'HomeAssistant-BibliaSk/0.1.0'}) as response:
            response.raise_for_status()
            chunks = []
            size = 0
            async for chunk in response.content.iter_chunked(65536):
                size += len(chunk)
                if size > 4_000_000:
                    raise ValueError('Chapter response is too large')
                chunks.append(chunk)
            html = b''.join(chunks).decode('utf-8')
    return await hass.async_add_executor_job(extract_text, html, passage)
