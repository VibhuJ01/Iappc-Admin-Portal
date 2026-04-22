#!/bin/bash

# Navigate to the working directory
cd /home/admin/Iappc-Admin-Portal || exit 1

# Activate the virtual environment
source iappc_admin_portal_venv/bin/activate

# Default number of workers for UAT
WORKERS=1

# Parse command-line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -w|--workers) WORKERS="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

echo "Starting Uvicorn with $WORKERS worker(s) on port 5576..."
gunicorn app:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:5576 \
    --workers "$WORKERS" \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --timeout 60 \
    --keep-alive 5 \
    --access-logfile - \
    --error-logfile -
