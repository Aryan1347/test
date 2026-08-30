#!/bin/bash
# Clone and build the POT provider server
git clone https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git /tmp/bgutil
cd /tmp/bgutil/server
npm ci
npx tsc

# Run the server in the background on port 4416
node build/main.js --port 4416 &