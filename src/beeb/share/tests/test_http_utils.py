import pytest

from beeb.share.http_utils import GET

@pytest.fixture
def bbc_url():
    return "https://bbc.co.uk"

@pytest.fixture
def nonexisting_url():
    return "https://doesnotexist.bbc.co.uk"

def test_GET_success(bbc_url):
    try:
        GET(bbc_url, raise_for_status=True)
    except Exception as e:
        raise e

def test_GET_fail(nonexisting_url):
    try:
        GET(nonexisting_url, raise_for_status=True)
    except Exception as e:
        pass
    else:
        raise ValueError("Should have errored on nonexisting URL")
