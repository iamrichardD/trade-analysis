import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from storage import CSVFileWriter, LogWriter, get_writer, ConfigurationError

@pytest.fixture
def sample_df():
    return pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

def test_csv_file_writer(sample_df):
    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        config = {"output_type": "file", "path": "/tmp"}
        writer = CSVFileWriter(config)
        writer.write(sample_df)
        mock_to_csv.assert_called_once()

def test_log_writer(sample_df):
    with patch("logging.info") as mock_log_info:
        config = {"output_type": "log"}
        writer = LogWriter()
        writer.write(sample_df)
        mock_log_info.assert_called_once_with(sample_df.to_string())

def test_get_writer_file():
    config = {"output_type": "file", "path": "/tmp"}
    writer = get_writer(config)
    assert isinstance(writer, CSVFileWriter)

def test_get_writer_log():
    config = {"output_type": "log"}
    writer = get_writer(config)
    assert isinstance(writer, LogWriter)

def test_get_writer_invalid_type():
    with pytest.raises(ConfigurationError):
        config = {"output_type": "invalid"}
        get_writer(config)

def test_get_writer_missing_type():
    with pytest.raises(ConfigurationError):
        config = {"path": "/tmp"}
        get_writer(config)

def test_csv_writer_missing_path():
    with pytest.raises(ConfigurationError):
        config = {"output_type": "file"}
        CSVFileWriter(config)
