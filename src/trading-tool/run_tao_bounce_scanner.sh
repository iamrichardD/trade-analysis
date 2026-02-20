podman run --rm \
  --security-opt seccomp=unconfined \
  -v /home/richard/scans:/scans:Z \
  localhost/tao-bounce-scanner:latest