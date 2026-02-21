# Tao of Trading Analysis Engine

Trading scanner that identifies high-probability setups (Bounce 2.0) using the TradingView Scanner API.

---

## ⚡ Quick Start

This project follows a **Zero-Host Policy**. All execution must occur inside a container.

### 1. Build the Container
```bash
podman build -t tao-scanner src/trading-tool/
```

### 2. Run a Bullish Scan (Log Output)
```bash
podman run --rm tao-scanner --output_type log --direction long
```

### 3. Run with Environment File (For SNS/Email Alerts)
```bash
podman run --rm --env-file .env tao-scanner --output_type email --sns_topic_arn "arn:aws:sns:..."
```

### 4. Execute Tests
```bash
podman build -f src/trading-tool/Containerfile.test -t tao-scanner-test src/trading-tool/
podman run --rm --security-opt seccomp=unconfined tao-scanner-test
```

> [!NOTE]
> **Security & Troubleshooting**: If you encounter `permission denied` or `seccomp` errors during build or run (common on some Linux distributions), append `--security-opt seccomp=unconfined` to your commands. This relaxes the default security profile to allow certain system calls (like `bdflush`) required by specific library dependencies.

---

## 🗝️ Secrets & Configuration

The engine requires two sets of credentials: **Infrastructure (Terraform)** for deployment and **Runtime (AWS)** for notifications.

### 1. Infrastructure (Proxmox Deployment)
Located in `src/trading-tool/deployment/terraform.tfvars`.

| Variable | Description |
| :--- | :--- |
| `proxmox_endpoint` | FQDN or IP of your Proxmox server |
| `proxmox_token_id` | API Token ID (e.g., `terraform@pve!tao`) |
| `proxmox_token_secret` | The secret portion of the Proxmox API token |
| `ssh_public_key` | Your SSH key for LXC container access |

### 2. Runtime (AWS SNS Notifications)
Passed via `.env` file during `podman run`.

| Variable | Description |
| :--- | :--- |
| `AWS_ACCESS_KEY_ID` | Access Key for the `tao-scanner-machine-account` |
| `AWS_SECRET_ACCESS_KEY` | Secret Key for the machine account |
| `AWS_DEFAULT_REGION` | AWS region (e.g., `us-east-1`) |
| `SNS_TOPIC_ARN` | The ARN created by Terraform (check `terraform output`) |

> [!TIP]
> See [SNS_NOTIFICATION_SETUP.md](src/trading-tool/SNS_NOTIFICATION_SETUP.md) for step-by-step instructions on generating these keys.

---

## 📘 The Deets

### What is this project?
This tool automates the "Bounce 2.0" strategy described in the `gem/dao-of-trading-technical-manual.md`. Instead of manually clicking through hundreds of charts on TradingView, this scanner queries thousands of stocks simultaneously and returns only those meeting strict institutional criteria.

### Why Bounce 2.0?
The Bounce 2.0 strategy focuses on "Action Zones"—areas where price is trending strongly but has temporarily pulled back to its 21-period moving average. These setups offer a high **Expectancy** and clear risk/reward targets.

### Why Podman / Containers?
We use Podman to ensure the scanner runs exactly the same on your laptop as it does on a Proxmox LXC server. It isolates the Python environment, preventing "it works on my machine" bugs and ensuring your host system remains clean.

---

## 🏛 Architecture & Data Flow

1.  **Query Engine**: Builds a complex SQL-like query for the TradingView API, filtering for liquidity (Market Cap > $1B), trend (ADX > 20, SMA200 alignment), and stacking EMAs.
2.  **Logic Layer**: Applies local filters that the API cannot calculate (e.g., precise "Action Zone" proximity and RSI(2) triggers).
3.  **Storage/Alerts**:
    - **CSV**: Saves results to `/scans/` for auditability.
    - **SNS**: Sends automated Markdown-formatted email alerts via AWS SNS.
4.  **Deployment**: Automated via Terraform to Proxmox LXC containers.

---

## 🔐 Security & Standards

- **Zero-Host Policy**: No Python/Pip execution on the host machine.
- **Least Privilege**: IAM policies for the scanner are restricted to `sns:Publish` on one specific topic ARN.
- **Strong Typing**: 100% Type Hint coverage (Mypy compliant).
- **SOLID Principles**: Decoupled DataWriters and modularized filter logic.

---

## 📂 Project Structure

- `src/trading-tool/`: Core scanner logic, container configs, and tests.
- `gem/`: The "Tao of Trading" technical manual (Strategy source of truth).
- `deployment/`: Terraform and SSH deployment scripts.
- `TODO.md` / `PROGRESS.md`: Current development roadmap.
