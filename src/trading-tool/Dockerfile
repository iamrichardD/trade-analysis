# Use the current stable Python slim image
FROM python:3.12-slim

# Set environment variables for non-interactive installs and timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=America/New_York

# Install system dependencies and timezone data
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and wrapper script
COPY tao_bounce_scanner.py .
COPY run_tao_bounce_scanner.sh .

# Ensure the shell script is executable
RUN chmod +x run_tao_bounce_scanner.sh

# The entrypoint runs the wrapper script
ENTRYPOINT ["/bin/bash", "./run_tao_bounce_scanner.sh"]
