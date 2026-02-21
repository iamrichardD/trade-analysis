import pytest
import pandas as pd
from moto import mock_aws
import boto3
from storage import SNSWriter, ConfigurationError, get_writer, ScannerConfig
from unittest.mock import patch

@pytest.fixture
def sns_setup():
    """
    Sets up a mocked SNS topic for testing.
    Why: Provides an isolated AWS-like environment to verify SNS interactions without actual cloud costs or side effects.
    """
    with mock_aws():
        sns = boto3.client("sns", region_name="us-east-1")
        topic = sns.create_topic(Name="test-topic")
        yield topic["TopicArn"]

def test_should_publish_to_sns_when_dataframe_is_not_empty(sns_setup):
    """
    Why: Verifies that the SNSWriter correctly formats and publishes data when results are found.
    Ensures that candidates identified by the scanner are actually broadcast.
    """
    topic_arn = sns_setup
    writer = SNSWriter(topic_arn, "us-east-1")
    df = pd.DataFrame({"symbol": ["AAPL", "MSFT"], "close": [150.0, 400.0]})
    
    with patch("logging.info") as mock_log:
        writer.write(df)
        # Check that the log message containing Message ID was printed
        assert any("SNS notification sent. Message ID:" in str(call) for call in mock_log.call_args_list)

def test_should_skip_publish_when_dataframe_is_empty(sns_setup):
    """
    Why: Prevents unnecessary/empty email notifications which would be noise for the user.
    """
    topic_arn = sns_setup
    writer = SNSWriter(topic_arn, "us-east-1")
    df = pd.DataFrame()
    
    with patch("logging.info") as mock_log:
        writer.write(df)
        mock_log.assert_called_with("No candidates found. Skipping email notification.")

def test_should_handle_sns_publish_error(sns_setup):
    """
    Why: Ensures the application doesn't crash if the notification system fails (Graceful Degradation).
    The scan should still be considered successful even if the alert fails.
    """
    topic_arn = sns_setup
    writer = SNSWriter(topic_arn, "us-east-1")
    df = pd.DataFrame({"symbol": ["AAPL"]})
    
    # Force an error by patching sns.publish
    with patch.object(writer.sns, "publish", side_effect=Exception("AWS Error")):
        with patch("logging.error") as mock_log:
            writer.write(df)
            mock_log.assert_called_with("Failed to send SNS notification: AWS Error")

def test_should_create_snswriter_from_factory():
    """
    Why: Verifies the factory correctly instantiates the SNSWriter with the right parameters.
    Ensures Dependency Inversion is properly implemented.
    """
    config = ScannerConfig(
        output_type="email",
        sns_topic_arn="arn:aws:sns:us-east-1:123456789012:my-topic",
        aws_region="us-east-1"
    )
    writer = get_writer(config)
    assert isinstance(writer, SNSWriter)
    assert writer.topic_arn == "arn:aws:sns:us-east-1:123456789012:my-topic"
    assert writer.region_name == "us-east-1"

def test_should_raise_error_when_topic_arn_missing_for_email_output():
    """
    Why: Prevents runtime failures by ensuring required configuration is present at startup.
    """
    config = {
        "output_type": "email",
        "aws_region": "us-east-1"
    }
    with pytest.raises(ConfigurationError, match="Missing 'sns_topic_arn' for 'email' output type"):
        get_writer(config)
