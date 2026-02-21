import pandas as pd
from abc import ABC, abstractmethod
import logging
from datetime import datetime
from typing import Optional, Literal, Dict, Any, Union
from dataclasses import dataclass

class ConfigurationError(Exception):
    """
    Exception raised for errors in the scanner configuration.
    Why: Allows calling code to catch configuration specific errors separately from runtime errors.
    """
    pass

@dataclass(frozen=True)
class ScannerConfig:
    """
    Configuration for the Tao of Trading Scanner.
    Why: Provides a strongly-typed, immutable configuration object to prevent runtime type errors 
    and ensuring all necessary config values are present.
    """
    output_type: Literal["file", "log"]
    direction: Literal["long", "short"] = "long"
    path: Optional[str] = None

class DataWriter(ABC):
    """
    Abstract base class for data writers.
    Why: Enforces the Interface Segregation Principle (SOLID), allowing different output strategies 
    (CSV, Database, Log) to be swapped without changing the scanner logic.
    """
    @abstractmethod
    def write(self, df: pd.DataFrame) -> None:
        """Writes the provided DataFrame to the configured output."""
        pass

class CSVFileWriter(DataWriter):
    """
    Writes scanner results to a CSV file.
    Why: Persists scan results for later analysis or auditing.
    """
    def __init__(self, path: str) -> None:
        self.path = path

    def write(self, df: pd.DataFrame) -> None:
        """Saves the DataFrame to a timestamped CSV file."""
        filename = f"tao_scan_{datetime.now().strftime('%Y%m%d')}.csv"
        full_path = f"{self.path}/{filename}"
        df.to_csv(full_path, index=False)
        logging.info(f"Scan complete. {len(df)} candidates found. Saved to {full_path}.")

class LogWriter(DataWriter):
    """
    Writes scanner results to the system log.
    Why: Useful for debugging, cloud logging streams, or quick manual checks in CLI.
    """
    def write(self, df: pd.DataFrame) -> None:
        """Logs the DataFrame as a string."""
        logging.info("\n" + df.to_string())

def get_writer(config: Union[ScannerConfig, Dict[str, Any]]) -> DataWriter:
    """
    Factory function to return the appropriate DataWriter based on configuration.
    Why: Decouples the creation of the writer from its usage (Dependency Inversion), 
    making the system more flexible and easier to test.
    """
    if isinstance(config, dict):
        output_type = config.get("output_type")
        direction = config.get("direction", "long")
        path = config.get("path")
    else:
        output_type = config.output_type
        direction = config.direction
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
