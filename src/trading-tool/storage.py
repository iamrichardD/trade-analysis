import pandas as pd
from abc import ABC, abstractmethod
import logging
from datetime import datetime

class ConfigurationError(Exception):
    pass

class DataWriter(ABC):
    @abstractmethod
    def write(self, df: pd.DataFrame):
        pass

class CSVFileWriter(DataWriter):
    def __init__(self, config: dict):
        if "path" not in config:
            raise ConfigurationError("Missing 'path' in config")
        self.path = config["path"]

    def write(self, df: pd.DataFrame):
        filename = f"tao_scan_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(f"{self.path}/{filename}", index=False)
        logging.info(f"Scan complete. {len(df)} candidates found. Saved to {self.path}/{filename}.")

class LogWriter(DataWriter):
    def write(self, df: pd.DataFrame):
        logging.info(df.to_string())

def get_writer(config: dict) -> DataWriter:
    if "output_type" not in config:
        raise ConfigurationError("Missing 'output_type' in config")

    output_type = config["output_type"]
    if output_type == "file":
        return CSVFileWriter(config)
    elif output_type == "log":
        return LogWriter()
    else:
        raise ConfigurationError(f"Invalid output_type: {output_type}")
