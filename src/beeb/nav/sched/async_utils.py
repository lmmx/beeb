import asyncio
import httpx
from aiostream import stream
from functools import partial
from pathlib import Path
from ...api.json_helpers import EpisodeMetadataPidJson

__all__ = ["fetch", "process", "async_fetch_urlset", "fetch_urls"]

async def fetch(session, url, raise_for_status=False):
    response = await session.get(str(url))
    if raise_for_status:
        response.raise_for_status()
    return response


async def process_soup(data, schedules, pbar=None, verbose=False):
    # Map the response back to the ChannelSchedule it came from in the schedules list
    sched = next(s for s in schedules if data.url == s.sched_url)
    # Save the soup for boiling later (using multiprocessing on entire listing)
    sched.frozen_soup = data.content.decode()
    if verbose:
        print({data.url: data})
    if pbar:
        pbar.update()


async def process_json(data, jsons, pbar=None, verbose=False):
    # Map the response back to the EpisodeMetadataPidJson it came from in the jsons list
    episode = next(e for (u, e) in jsons.items() if data.url == u)
    # Save the JSON for later (using multiprocessing on entire listing)
    episode.frozen_data = EpisodeMetadataPidJson.from_json(
        json=data.content.decode(), pid=episode.pid, load_string=True
    )
    if verbose:
        print({data.url: data})
    if pbar:
        pbar.update()


async def async_fetch_urlset(urls, schedules, pbar=None, verbose=False, use_http2=True):
    async with httpx.AsyncClient(http2=use_http2) as session:
        ws = stream.repeat(session)
        xs = stream.zip(ws, stream.iterate(urls))
        ys = stream.starmap(xs, fetch, ordered=False, task_limit=20) # 30 is similar IDK
        process = partial(process_soup, schedules=schedules, pbar=pbar, verbose=verbose)
        zs = stream.map(ys, process)
        return await zs

def fetch_schedules(urls, schedules, pbar=None, verbose=False):
    return asyncio.run(async_fetch_urlset(urls, schedules, pbar, verbose))


# do not use http2, it's throwing exceptions see #6 for tracebacks and links
async def async_fetch_episodes(listings, pbar=None, verbose=False, use_http2=False):
    jsons = dict(zip(listings.broadcasts_urlset, listings.all_broadcasts))
    limits = httpx.Limits(max_keepalive_connections=20)
    async with httpx.AsyncClient(http2=use_http2, limits=limits) as session:
        ws = stream.repeat(session)
        xs = stream.zip(ws, stream.iterate(listings.broadcasts_urlset))
        ys = stream.starmap(xs, fetch, ordered=False, task_limit=20) # 20 is optimal
        process = partial(process_json, jsons=jsons, pbar=pbar, verbose=verbose)
        zs = stream.map(ys, process)
        return await zs


def fetch_episode_metadata(listings, pbar=None, verbose=False):
    return asyncio.run(async_fetch_episodes(listings, pbar, verbose))
