import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from storage import CSVFileWriter, LogWriter, get_writer, ConfigurationError, ScannerConfig
from typing import Generator

@pytest.fixture
def sample_df() -> pd.DataFrame:
    return pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

def test_csv_file_writer(sample_df: pd.DataFrame) -> None:
    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        writer = CSVFileWriter("/tmp")
        writer.write(sample_df)
        mock_to_csv.assert_called_once()

def test_log_writer(sample_df: pd.DataFrame) -> None:
    with patch("logging.info") as mock_log_info:
        writer = LogWriter()
        writer.write(sample_df)
        # LogWriter now adds a newline prefix for better formatting
        mock_log_info.assert_called_once_with("\n" + sample_df.to_string())

def test_get_writer_file() -> None:
    config = ScannerConfig(output_type="file", path="/tmp")
    writer = get_writer(config)
    assert isinstance(writer, CSVFileWriter)
    assert writer.path == "/tmp"

def test_get_writer_log() -> None:
    config = ScannerConfig(output_type="log")
    writer = get_writer(config)
    assert isinstance(writer, LogWriter)

def test_get_writer_invalid_type() -> None:
    # Use dict to bypass type checking for the invalid type test
    with pytest.raises(ConfigurationError):
        config = {"output_type": "invalid"}
        get_writer(config)

def test_get_writer_missing_type() -> None:
    with pytest.raises(ConfigurationError):
        config = {"path": "/tmp"}
        get_writer(config)

def test_get_writer_missing_path() -> None:
    with pytest.raises(ConfigurationError):
        config = ScannerConfig(output_type="file")
        get_writer(config)
