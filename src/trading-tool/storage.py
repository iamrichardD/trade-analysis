import pandas as pd
from abc import ABC, abstractmethod
import logging
import boto3
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
    output_type: Literal["file", "log", "email"]
    direction: Literal["long", "short"] = "long"
    path: Optional[str] = None
    sns_topic_arn: Optional[str] = None
    aws_region: Optional[str] = "us-east-1"

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

class SNSWriter(DataWriter):
    """
    Publishes scanner results as a Markdown table via AWS SNS.
    Why: Enables automated email alerts when high-potential setups are identified, 
    reducing the need for manual check in the terminal.
    """
    def __init__(self, topic_arn: str, region_name: str) -> None:
        self.topic_arn = topic_arn
        self.region_name = region_name
        self.sns = boto3.client("sns", region_name=region_name)

    def write(self, df: pd.DataFrame) -> None:
        """Publishes the DataFrame results to the SNS topic as a Markdown table."""
        if df.empty:
            logging.info("No candidates found. Skipping email notification.")
            return

        # Format scan date for subject line
        scan_date = datetime.now().strftime('%Y-%m-%d')
        subject = f"Tao Scan Results - {scan_date} ({len(df)} candidates)"

        # Convert DataFrame to Markdown table
        message = f"## Tao of Trading - Scan Results ({scan_date})\n\n"
        message += df.to_markdown(index=False)
        message += "\n\n---\n*Sent via Tao Scanner Machine Account*"

        try:
            response = self.sns.publish(
                TopicArn=self.topic_arn,
                Subject=subject,
                Message=message
            )
            logging.info(f"SNS notification sent. Message ID: {response.get('MessageId')}")
        except Exception as e:
            logging.error(f"Failed to send SNS notification: {str(e)}")

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
        sns_topic_arn = config.get("sns_topic_arn")
        aws_region = config.get("aws_region", "us-east-1")
    else:
        output_type = config.output_type
        direction = config.direction
        path = config.path
        sns_topic_arn = config.sns_topic_arn
        aws_region = config.aws_region

    if not output_type:
        raise ConfigurationError("Missing 'output_type' in config")

    if output_type == "file":
        if not path:
            raise ConfigurationError("Missing 'path' for 'file' output type")
        return CSVFileWriter(path)
    elif output_type == "log":
        return LogWriter()
    elif output_type == "email":
        if not sns_topic_arn:
            raise ConfigurationError("Missing 'sns_topic_arn' for 'email' output type")
        return SNSWriter(sns_topic_arn, aws_region or "us-east-1")
    else:
        raise ConfigurationError(f"Invalid output_type: {output_type}")
