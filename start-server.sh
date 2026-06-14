#!/bin/bash
# AICL Web Editor Server Launcher
cd /home/z/my-project
export NODE_ENV=production
export PORT=3000
export HOSTNAME=0.0.0.0

# Kill any existing server
pkill -f "node.*standalone/server.js" 2>/dev/null
sleep 2

# Start the server - this process stays alive
echo "Starting AICL Web Editor..."
exec node .next/standalone/server.js
