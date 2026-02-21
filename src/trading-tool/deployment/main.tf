terraform {
  required_providers {
    proxmox = {
      source  = "bpg/proxmox"
      version = "0.78.2"
    }
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "proxmox" {
  endpoint  = "https://${var.proxmox_endpoint}:8006/"
  api_token = "${var.proxmox_token_id}=${var.proxmox_token_secret}"
  insecure  = true
}

provider "aws" {
  region = var.aws_region
}

# SNS Infrastructure for Scanner Alerts
resource "aws_sns_topic" "scanner_alerts" {
  name = "tao-scanner-alerts"
}

resource "aws_sns_topic_subscription" "email_subscription" {
  for_each  = toset(var.alert_emails)
  topic_arn = aws_sns_topic.scanner_alerts.arn
  protocol  = "email"
  endpoint  = each.value
}

# IAM Machine Account for Tao Scanner
resource "aws_iam_user" "tao_scanner" {
  name = "tao-scanner-machine-account"
  tags = {
    System = "Trading Analysis Engine"
  }
}

resource "aws_iam_access_key" "tao_scanner" {
  user = aws_iam_user.tao_scanner.name
}

resource "aws_iam_policy" "sns_publish" {
  name        = "TaoScannerSNSPublishPolicy"
  description = "Allows publishing specifically to the tao-scanner-alerts SNS topic"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["sns:Publish"]
        Effect   = "Allow"
        Resource = [aws_sns_topic.scanner_alerts.arn]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "tao_scanner_publish" {
  user       = aws_iam_user.tao_scanner.name
  policy_arn = aws_iam_policy.sns_publish.arn
}

resource "proxmox_virtual_environment_container" "tao_scanner_lxc" {
  node_name = "pve" # Your Proxmox node name
  vm_id     = 200

  initialization {
    hostname = "tao-scanner"
    ip_config {
      ipv4 {
        address = "dhcp"
      }
    }
    user_account {
      keys = [var.ssh_public_key]
    }
  }

  cpu { cores = 1 }
  memory { dedicated = 512 } # Memory optimized

  operating_system {
    template_file_id = "local:vztmpl/ubuntu-22.04-standard_22.04-1_amd64.tar.zst"
    type             = "ubuntu"
  }

  # Provisioning the scanner environment
  provisioner "remote-exec" {
    inline = [
      "mkdir -p /home/richard/scans",
      "chmod 755 /home/richard/run_tao_bounce_scanner.sh",
      # Inject the cron configuration directly
      "echo '15 9 * * 1-5 root /usr/bin/podman run --rm -v /home/richard/scans:/scans:Z tao_bounce_scanner:latest' | sudo tee /etc/cron.d/tao_scanner",
      "sudo chmod 644 /etc/cron.d/tao_scanner"
    ]
  }
}
