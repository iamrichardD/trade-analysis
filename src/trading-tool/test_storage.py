import pandas as pd
import pytest
from unittest.mock import patch, MagicMock
from storage import CSVFileWriter, LogWriter, get_writer, ConfigurationError, ScannerConfig
from typing import Generator

@pytest.fixture
def sample_df() -> pd.DataFrame:
    """
    Provides a simple DataFrame for testing writers.
    Why: Ensures tests use consistent data structure without repeating setup code.
    """
    return pd.DataFrame({"col1": [1, 2], "col2": [3, 4]})

def test_csv_file_writer(sample_df: pd.DataFrame) -> None:
    """
    Verifies that CSVFileWriter correctly calls pandas.to_csv.
    Why: To ensure data is actually persisted to disk when 'file' output is selected.
    """
    with patch("pandas.DataFrame.to_csv") as mock_to_csv:
        writer = CSVFileWriter("/tmp")
        writer.write(sample_df)
        mock_to_csv.assert_called_once()

def test_log_writer(sample_df: pd.DataFrame) -> None:
    """
    Verifies that LogWriter logs the data to the system logger.
    Why: To ensure data is visible in logs (stdout/stderr) when 'log' output is selected.
    """
    with patch("logging.info") as mock_log_info:
        writer = LogWriter()
        writer.write(sample_df)
        # LogWriter adds a newline prefix for better formatting in logs
        mock_log_info.assert_called_once_with("\n" + sample_df.to_string())

def test_get_writer_file() -> None:
    """
    Verifies that get_writer returns a CSVFileWriter when configured for 'file'.
    Why: Factory method must correctly map configuration to implementation.
    """
    config = ScannerConfig(output_type="file", path="/tmp")
    writer = get_writer(config)
    assert isinstance(writer, CSVFileWriter)
    assert writer.path == "/tmp"

def test_get_writer_log() -> None:
    """
    Verifies that get_writer returns a LogWriter when configured for 'log'.
    Why: Factory method must correctly map configuration to implementation.
    """
    config = ScannerConfig(output_type="log")
    writer = get_writer(config)
    assert isinstance(writer, LogWriter)

def test_get_writer_invalid_type() -> None:
    """
    Verifies that ConfigurationError is raised for unknown output types.
    Why: Fail fast on invalid configuration to prevent runtime errors later.
    """
    # Use dict to bypass type checking for the invalid type test simulation
    with pytest.raises(ConfigurationError):
        config = {"output_type": "invalid"} # type: ignore
        get_writer(config)

def test_get_writer_missing_type() -> None:
    """
    Verifies that ConfigurationError is raised when output_type is missing.
    Why: Configuration validation.
    """
    with pytest.raises(ConfigurationError):
        config = {"path": "/tmp"} # type: ignore
        get_writer(config)

def test_get_writer_missing_path() -> None:
    """
    Verifies that ConfigurationError is raised when path is missing for 'file' output.
    Why: File output requires a destination path.
    """
    with pytest.raises(ConfigurationError):
        config = ScannerConfig(output_type="file")
        get_writer(config)
