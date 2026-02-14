#!/bin/bash
cd "$(dirname "$0")"
echo "Starting debug install at $(date)" > install.log
pwd >> install.log
echo "Node version: $(node -v)" >> install.log
echo "NPM version: $(npm -v)" >> install.log
echo "Yarn version: $(yarn -v)" >> install.log

echo "Running npm install..." >> install.log
npm install >> install.log 2>&1
EXIT_CODE=$?
echo "npm install finished with exit code $EXIT_CODE" >> install.log
