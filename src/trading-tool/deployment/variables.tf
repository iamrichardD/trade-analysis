variable "proxmox_endpoint" {
  description = "The FQDN or IP of the Proxmox server"
  type        = string
}

variable "proxmox_token_secret" {
  description = "The secret part of the Proxmox API token"
  type        = string
  sensitive   = true # Prevents the secret from being logged in plain text
}

variable "proxmox_token_id" {
  description = "The full Token ID (e.g., terraform-prov@pve!tao-scanner)"
  type        = string
  default     = "terraform-prov@pve!tao-scanner"
}

variable "ssh_public_key" {
  description = "The SSH public key string for LXC access"
  type        = string
}

variable "aws_region" {
  description = "AWS region for SNS topic"
  type        = string
  default     = "us-east-1"
}

variable "alert_emails" {
  description = "List of email addresses to subscribe to scanner alerts"
  type        = list(string)
  default     = []
}
