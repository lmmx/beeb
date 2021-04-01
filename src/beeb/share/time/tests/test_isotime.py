import pytest

from beeb.share.multiproc_utils import batch_multiprocess
from beeb.share.multiproc_utils import batch_multiprocess_with_return

def function_to_return():
    x = 1 + 1
    return x

@pytest.fixture
def func_list():
    "A 3 item-long list of functions which each return the value 2 when called"
    return [function_to_return for _ in range(3)]

def test_multiproc(func_list):
    x = batch_multiprocess(func_list)
    assert x is None

def test_multiproc_with_return(func_list):
    "Compute the 3 functions that each return the value 2, and verify the total is 6"
    values = []
    values = batch_multiprocess_with_return(func_list, pool_results=values, show_progress=False)
    assert sum(values) == 6
