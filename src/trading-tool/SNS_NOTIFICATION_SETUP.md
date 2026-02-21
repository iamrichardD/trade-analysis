# AWS SNS Notification Setup Guide

This guide describes how to configure and deploy the AWS SNS notification system for the Tao of Trading scanner.

## 1. Infrastructure Deployment (Terraform)

The Terraform configuration in `deployment/` creates the necessary AWS resources.

1.  **Configure Variables**:
    Update your `terraform.tfvars` (or pass via CLI) with the alert email addresses:
    ```hcl
    alert_emails = ["your-email@example.com"]
    aws_region   = "us-east-1"
    ```

2.  **Deploy**:
    ```bash
    cd deployment
    terraform init
    terraform apply
    ```

3.  **Confirm Subscriptions**:
    AWS will send a confirmation email to each address in `alert_emails`. Each recipient **must click the "Confirm Subscription" link** before they can receive alerts.

4.  **Retrieve Machine Credentials**:
    After deployment, retrieve the IAM access key and secret for the `tao-scanner-machine-account`.
    ```bash
    terraform output -json | jq '.tao_scanner_access_key'
    ```

## 2. Secure Credential Injection (Podman)

For security, NEVER hardcode AWS credentials. Use Podman environment files or secrets.

### Option A: Environment File (.env) - Recommended for LXC
Create a `.env` file on the scanner host (e.g., in `/home/richard/.env`):
```bash
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=us-east-1
SNS_TOPIC_ARN=arn:aws:sns:us-east-1:123456789012:tao-scanner-alerts
```

Update your `podman run` command in the cron job/timer:
```bash
podman run --rm --env-file /home/richard/.env ...
```

### Option B: Podman Secrets (More Secure)
If your Podman environment supports secrets:
```bash
echo "AKIA..." | podman secret create aws_access_key -
echo "..." | podman secret create aws_secret_key -
```

## 3. Application Configuration

To enable email notifications, update the `ScannerConfig` in your execution script:

```python
config = ScannerConfig(
    output_type="email",
    sns_topic_arn="arn:aws:sns:us-east-1:123456789012:tao-scanner-alerts",
    aws_region="us-east-1"
)
```

The scanner will format results as a Markdown table and send them via the configured SNS topic.
