# TAO Bounce Scanner

A specialized scanning utility designed to run on a Pacific Time host while adhering to an Eastern Time schedule (9:00 AM and 9:30 AM ET). This project is structured for repeatable DevSecOps automation.

## Project Structure

| File | Description |
| :--- | :--- |
| `tao_bounce_scanner.py` | The core Python logic for the scanner. |
| `run_tao_bounce_scanner.sh` | Bash entry point/wrapper for environment setup and execution. |
| `requirements.txt` | Python dependencies. |
| `Dockerfile` | Containerization for platform-independent execution. |
| `tao-scanner.service` | Systemd service definition (The "What"). |
| `tao-scanner.timer` | Systemd timer definition (The "When"). |

---

## 1. Local Setup (Ubuntu Workstation)

Ensure you have the current LTS dependencies:
```bash
sudo apt update && sudo apt install -y python3-pip
pip install -r requirements.txt
chmod +x run_tao_bounce_scanner.sh

```

## 2. Local Setup & Deployment

Manual Installation (Ubuntu Workstation)
  * Permissions: chmod +x run_tao_bounce_scanner.sh
  * Deploy Files:

```bash
sudo cp run_tao_bounce_scanner.sh /usr/local/bin/
sudo cp tao-scanner.service /etc/systemd/system/
sudo cp tao-scanner.timer /etc/systemd/system/
```

## 3. Enable Automation:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now tao-scanner.timer
```

### Containerized Execution (Docker)

```bash
docker build -t tao-bounce-scanner .
docker run --rm tao-bounce-scanner
```

### Containerized Execution (Podman)

On newer Linux kernels (6.8+), Podman may encounter a seccomp error related to the `bdflush` syscall (`error adding seccomp filter rule for syscall bdflush: permission denied`). 

Use the following commands to build and run with a workaround:

```bash
# Build
podman build --security-opt seccomp=unconfined -t tao-bounce-scanner .

# Run
podman run --rm --security-opt seccomp=unconfined tao-bounce-scanner
```

### 4. Maintenance & Observability Guide
Observability: Monitoring Health
Since this runs twice a morning, use these commands to verify execution:

Check Next Run: `systemctl list-timers tao-scanner.timer`

This confirms the next scheduled run in Eastern Time.

Audit Logs: `journalctl -u tao-scanner.service -o short-precise`

Provides millisecond-accurate timestamps and logs for every execution.

Success Verification: `systemctl status tao-scanner.service`

Look for `status=0/SUCCESS` to confirm the Python script finished correctly.

Maintenance: Troubleshooting
Manual Execution: To trigger a scan immediately for testing:
`sudo systemctl start tao-scanner.service`

Updating Schedules: If you modify the .timer file, you must reload the daemon:
`sudo systemctl daemon-reload && sudo systemctl restart tao-scanner.timer`

Log Rotation: The service logs to `journald`. Ensure your workstation's journal is configured to rotate to prevent disk space issues.