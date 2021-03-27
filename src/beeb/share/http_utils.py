import httpx
from h2.exceptions import ProtocolError

__all__ = ["GET", "async_errors"]

def GET(url, raise_for_status=True):
    response = httpx.get(url)
    if raise_for_status:
        response.raise_for_status()
    return response

async_errors = (httpx.RemoteProtocolError, ProtocolError)
