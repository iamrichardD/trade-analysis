import pandas as pd
from abc import ABC, abstractmethod
import logging
from datetime import datetime
from typing import Optional, Literal, Dict, Any, Union
from dataclasses import dataclass

class ConfigurationError(Exception):
    """Exception raised for errors in the scanner configuration."""
    pass

@dataclass(frozen=True)
class ScannerConfig:
    """Configuration for the Tao of Trading Scanner."""
    output_type: Literal["file", "log"]
    path: Optional[str] = None

class DataWriter(ABC):
    """Abstract base class for data writers."""
    @abstractmethod
    def write(self, df: pd.DataFrame) -> None:
        """Writes the provided DataFrame to the configured output."""
        pass

class CSVFileWriter(DataWriter):
    """Writes scanner results to a CSV file."""
    def __init__(self, path: str) -> None:
        self.path = path

    def write(self, df: pd.DataFrame) -> None:
        """Saves the DataFrame to a timestamped CSV file."""
        filename = f"tao_scan_{datetime.now().strftime('%Y%m%d')}.csv"
        full_path = f"{self.path}/{filename}"
        df.to_csv(full_path, index=False)
        logging.info(f"Scan complete. {len(df)} candidates found. Saved to {full_path}.")

class LogWriter(DataWriter):
    """Writes scanner results to the system log."""
    def write(self, df: pd.DataFrame) -> None:
        """Logs the DataFrame as a string."""
        logging.info("\n" + df.to_string())

def get_writer(config: Union[ScannerConfig, Dict[str, Any]]) -> DataWriter:
    """
    Factory function to return the appropriate DataWriter based on configuration.
    Supports both ScannerConfig objects and legacy dictionaries for backward compatibility.
    """
    if isinstance(config, dict):
        output_type = config.get("output_type")
        path = config.get("path")
    else:
        output_type = config.output_type
        path = config.path

    if not output_type:
        raise ConfigurationError("Missing 'output_type' in config")

    if output_type == "file":
        if not path:
            raise ConfigurationError("Missing 'path' for 'file' output type")
        return CSVFileWriter(path)
    elif output_type == "log":
        return LogWriter()
    else:
        raise ConfigurationError(f"Invalid output_type: {output_type}")
