import httpx

__all__ = []

def GET(url, raise_for_status=True):
    response = httpx.get(url)
    if raise_for_status:
        response.raise_for_status()
    return response
