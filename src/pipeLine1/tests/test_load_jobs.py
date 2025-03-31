import os
import pytest
import pandas as pd
from unittest import mock
from unittest.mock import MagicMock, patch
from pymongo.errors import BulkWriteError

# Helper to reload the script (important if testing multiple exit scenarios)
def import_and_reload():
    import importlib
    import load_jobs
    importlib.reload(load_jobs)

# ------- TEST: Successful MongoDB flow -------
@patch("builtins.print")  # to silence print (optional)
@patch("pymongo.MongoClient")
@patch("pandas.read_csv")
@patch("os.path.exists")
@patch.dict(os.environ, {"url": "mongodb://mock-url"})
def test_successful_run(mock_exists, mock_read_csv, mock_mongo, mock_print):
    mock_exists.return_value = True
    mock_read_csv.return_value = pd.DataFrame([{"role": "Dev"}, {"role": "Analyst"}])

    mock_collection = MagicMock()
    mock_collection.delete_many.return_value.deleted_count = 2
    mock_collection.find.return_value = [{"role": "Dev"}, {"role": "Analyst"}]

    mock_db = MagicMock()
    mock_db.jobsCollection = mock_collection

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.jobsDB = mock_db
    mock_client.admin.command.return_value = {"ok": 1}

    mock_mongo.return_value = mock_client

    import_and_reload()

    mock_collection.insert_many.assert_called_once()
    mock_collection.delete_many.assert_called_once()
    mock_collection.find.assert_called_once()

# ------- TEST: Missing MongoDB URL -------
@patch.dict(os.environ, {}, clear=True)
def test_missing_env_variable():
    with pytest.raises(SystemExit):
        import_and_reload()

# ------- TEST: CSV file not found -------
@patch("os.path.exists", return_value=False)
@patch.dict(os.environ, {"url": "mongodb://mock-url"})
def test_missing_csv(mock_exists):
    with pytest.raises(SystemExit):
        import_and_reload()

# ------- TEST: Error reading CSV -------
@patch("os.path.exists", return_value=True)
@patch("pandas.read_csv", side_effect=Exception("CSV corrupted"))
@patch.dict(os.environ, {"url": "mongodb://mock-url"})
def test_csv_read_error(mock_read, mock_exists):
    with pytest.raises(SystemExit):
        import_and_reload()

# ------- TEST: BulkWriteError on insert -------
@patch("os.path.exists", return_value=True)
@patch("pandas.read_csv", return_value=pd.DataFrame([{"job": "Data"}]))
@patch("pymongo.MongoClient")
@patch.dict(os.environ, {"url": "mongodb://mock-url"})
def test_bulk_write_error(mock_mongo, mock_read_csv, mock_exists):
    mock_collection = MagicMock()
    mock_collection.delete_many.return_value.deleted_count = 1
    mock_collection.insert_many.side_effect = BulkWriteError("Mock insert error")
    mock_collection.find.return_value = []

    mock_db = MagicMock()
    mock_db.jobsCollection = mock_collection

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.jobsDB = mock_db
    mock_client.admin.command.return_value = {"ok": 1}

    mock_mongo.return_value = mock_client

    import_and_reload()
    mock_collection.insert_many.assert_called_once()
