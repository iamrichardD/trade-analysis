#!/bin/bash

# Check if all arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: $0 <PROXMOX_ENDPOINT> <TOKEN_SECRET> <SSH_KEY_PATH>"
    echo "Example: $0 \"proxmox.iamrichardd.com\" \"secret-abc\" \"~/.ssh/id_ed25519.pub\""
    exit 1
fi

ENDPOINT=$1
SECRET=$2
KEY_PATH=$3

echo "--- Pre-Flight Validation ---"
# 1. Ping Check
if ! ping -c 1 -W 2 "$ENDPOINT" > /dev/null 2>&1; then
    echo "Error: Host $ENDPOINT is unreachable via ICMP (Ping)."
    exit 1
fi

# 2. Port 8006 Check (Proxmox API)
if ! nc -z -w 3 "$ENDPOINT" 8006; then
    echo "Error: Proxmox API port 8006 is closed on $ENDPOINT."
    exit 1
fi
echo "Connectivity Verified."

# 2. SSH Key Validation
if [ ! -f "$KEY_PATH" ]; then
    echo "Error: SSH Key file not found at $KEY_PATH"
    exit 1
fi
SSH_KEY_CONTENT=$(cat "$KEY_PATH")

echo "--- Initializing Terraform ---"
terraform init

echo "--- Deploying Tao Scanner to $ENDPOINT ---"
terraform apply -auto-approve\
  -var="proxmox_endpoint=$ENDPOINT" \
  -var="proxmox_token_secret=$SECRET" \
  -var="ssh_public_key=$SSH_KEY_CONTENT"

echo "--- Deployment Cycle Complete ---"
