import asyncio
import httpx
from aiostream import stream
import aiofiles
from functools import partial
from pathlib import Path

__all__ = ["fetch_urlset"]

async def fetch(session, url, raise_for_status=False):
    response = await session.get(str(url))
    if raise_for_status:
        response.raise_for_status()
    return response


async def process(data, download_dir, pbar=None, verbose=False):
    if not download_dir.exists():
        download_dir.mkdir(parents=True)
    filename = Path(str(data.url)).name
    download_filepath = download_dir / filename
    async with aiofiles.open(download_filepath, "wb") as f:
        await f.write(data.content)
    if verbose:
        print({data.url: data})
    if pbar:
        pbar.update()


async def async_fetch_urlset(urls, download_dir, pbar=None, verbose=False):
    async with httpx.AsyncClient(http2=True) as session:
        ws = stream.repeat(session)
        xs = stream.zip(ws, stream.iterate(urls))
        ys = stream.starmap(xs, fetch, ordered=False, task_limit=10)
        process_download = partial(
            process, download_dir=download_dir, pbar=pbar, verbose=verbose
        )
        zs = stream.map(ys, process_download)
        return await zs


def fetch_urlset(urlset, download_dir, pbar=None, verbose=False):
    return asyncio.run(async_fetch_urlset(urlset, download_dir, pbar, verbose))
