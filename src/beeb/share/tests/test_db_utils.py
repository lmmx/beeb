import pytest

from beeb.share.db_utils import CatalogueDB

@pytest.fixture
def db():
    return CatalogueDB()

@pytest.fixture
def demo_station():
    return "r4"

@pytest.fixture
def demo_pid():
    return "b006qj9z"

def test_db_connect(db):
    db.connect()

def test_db_exists(db):
    assert db.exists()

def test_present_station(db, demo_station):
    assert db.has_station(demo_station)

def test_absent_station(db):
    assert not db.has_station("r")

def test_null_station(db):
    assert not db.has_station("")

def test_programme_retrieval_multi(db, demo_station):
    results = db.retrieve_station(demo_station)
    assert results
    assert len(results) > 0

def test_programme_retrieval_mono(db, demo_station):
    result = db.retrieve_station(demo_station, fetch_all=False)
    assert isinstance(result, tuple)

def test_pid_retrieve(db, demo_pid):
    result = db.retrieve_pid(demo_pid)

# Don't test insertion to avoid accidentally mutating shipped DB, save that for
# integration/functional tests that consider creation/deletion of DB and failure cases
