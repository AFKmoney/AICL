#!/bin/bash
# AICL Server Watchdog - keeps the server alive
LOG="/tmp/aicl-watchdog.log"

while true; do
    echo "[$(date)] Starting AICL server..." >> "$LOG"
    cd /home/z/my-project
    export NODE_ENV=production
    export PORT=3000
    export HOSTNAME=0.0.0.0
    
    node .next/standalone/server.js >> "$LOG" 2>&1
    EXIT_CODE=$?
    echo "[$(date)] Server exited with code $EXIT_CODE, restarting in 3s..." >> "$LOG"
    sleep 3
done
