import pytest
import mongomock
from app.infrastructure.db.mongo_client import MongoDB

@pytest.fixture
def mongo_mock():
    # Pakai mongomock untuk fake MongoDB (tidak konek beneran)
    mock_uri = "mongodb://localhost:27017/test_db"
    db_name = "test_db"
    # Overwrite client_class dengan mongomock.MongoClient
    mongo = MongoDB(uri=mock_uri, db_name=db_name, client_class=mongomock.MongoClient)
    mongo.connect()
    yield mongo
    # Cleanup, mongomock tidak butuh cleanup khusus

def test_connection_success(mongo_mock):
    assert mongo_mock.client is not None
    assert mongo_mock.db.name == "test_db"

def test_insert_and_find(mongo_mock):
    col = mongo_mock.get_collection("users")
    user = {"name": "alice", "age": 30}
    result = col.insert_one(user)
    assert result.inserted_id is not None

    # Cari user
    found = col.find_one({"name": "alice"})
    assert found is not None
    assert found["age"] == 30

def test_get_db_and_collection(mongo_mock):
    db = mongo_mock.get_db()
    assert db.name == "test_db"
    col = mongo_mock.get_collection("abc")
    assert col.name == "abc"

def test_extract_db_name_from_uri():
    from app.infrastructure.db.mongo_client import MongoDB
    uri1 = "mongodb://localhost:27017/mydb"
    uri2 = "mongodb+srv://user:pass@host/mydb?retryWrites=true&w=majority"
    assert MongoDB._extract_db_name(uri1) == "mydb"
    assert MongoDB._extract_db_name(uri2) == "mydb"

# def test_get_db_name_from_config(monkeypatch):
#     monkeypatch.setenv("DB_NAME", "env_db")
#     from app.infrastructure.db.mongo_client import MongoDB
#     assert MongoDB._get_db_name_from_config() == "env_db"
