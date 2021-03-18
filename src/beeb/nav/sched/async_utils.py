import asyncio
import httpx
from aiostream import stream
from functools import partial
from pathlib import Path

__all__ = ["fetch", "process", "async_fetch_urlset", "fetch_urls"]

async def fetch(session, url, raise_for_status=False):
    response = await session.get(str(url))
    if raise_for_status:
        response.raise_for_status()
    return response


async def process(data, schedules, pbar=None, verbose=False):
    # Map the response back to the ChannelSchedule it came from in the schedules list
    sched = next(s for s in schedules if data.url == s.sched_url)
    # Save the soup for boiling later (using multiprocessing on entire listing)
    sched.frozen_soup = data.content.decode()
    if verbose:
        print({data.url: data})
    if pbar:
        pbar.update()


async def async_fetch_urlset(urls, schedules, pbar=None, verbose=False, use_http2=True):
    async with httpx.AsyncClient(http2=use_http2) as session:
        ws = stream.repeat(session)
        xs = stream.zip(ws, stream.iterate(urls))
        ys = stream.starmap(xs, fetch, ordered=False, task_limit=30)
        process_data = partial(process, schedules=schedules, pbar=pbar, verbose=verbose)
        zs = stream.map(ys, process_data)
        return await zs

def fetch_schedules(urls, schedules, pbar=None, verbose=False):
    return asyncio.run(async_fetch_urlset(urls, schedules, pbar, verbose))

