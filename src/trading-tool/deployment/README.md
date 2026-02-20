# Tao of Trading: Fiduciary Risk Manager Deployment

This repository contains the Infrastructure as Code (IaC) and automation scripts to deploy a containerized stock scanner across Ubuntu workstations and Proxmox homelab environments.

## 📋 Overview
The system executes the **Bounce 2.0** strategy as defined by Simon Ree. It identifies high-probability mean-reversion setups in the US Equities market and outputs the results to a CSV for LLM Knowledge Base ingestion.

## 🏗️ Deployment Content
* `tao_bounce_scanner.py`: Type-safe Python scanner using TradingView API.
* `Containerfile`: OCI-compliant container definition for Podman/Docker.
* `main.tf`: Terraform configuration for Proxmox LXC provisioning.
* `variables.tf`: Decoupled variable declarations for security.
* `deploy_tao_scanner.sh`: Wrapper script with pre-flight network validation.

## 🚀 Execution Guide
### Prerequisites
1. **Podman** installed on the host.
2. **Terraform** (v1.5+) installed.
3. **Proxmox API Token** generated with `VM.Allocate` and `Datastore.Allocate` permissions.
4. **SSH Key Pair** (ED25519 recommended).

### Steps
1. **Prepare your environment:**
   ```bash
   chmod +x *.sh

2. **Deploy via Terraform Wrapper:** Run the deployment script by passing the endpoint, secret, and the path to your public key:

```bash
   ./deploy_tao_scanner.sh "proxmox.local" "your-secret" "~/.ssh/id_ed25519.pub"
```

## 🛡️ Best Practices
* **Fiduciary Warnings:** The scanner automatically filters out tickers with earnings reports scheduled within 14 days.
* **Security:** Never commit the terraform.tfstate file if it contains sensitive plan data. Use a .gitignore.  Marking the API secret as `sensitive` in Terraform ensures it is redacted from all logs.
* **Resource Optimization:** The LXC is configured for 512MB RAM. Do not increase this unless the ticker shortlist exceeds 5,000 items.
* **Storage:** All scans are written to the host via a Bind Mount (/scans). This ensures data persistence even if the container is destroyed.
* **Key Management:** Using a variable for the SSH key allows different team members (or different workstations) to deploy the same infrastructure without modifying the source code.

> [!WARNING]
> **ACCESS RISK:** Ensure the SSH key you provide is the one stored on the machine you intend to use for maintenance. If you lose access to this key, you will be locked out of the LXC container and will need to destroy/redeploy.

## 📊 Example Prompt for Gemini Gem
"Using the attached tao_scan_YYYYMMDD.csv, identify the top 3 tickers with an ADX > 25. Verify the 50% premium stop-loss requirement for a long call on the highest-ranked candidate."
