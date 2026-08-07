#!/usr/bin/env bash
# Install system dependencies for Playwright
apt-get update && apt-get install -y \
    libgtk-4-1 \
    libgraphene-1.0-0 \
    libgstreamer1.0-0 \
    libgstgl-1.0-0 \
    libgstcodecparsers1.0-0 \
    libmanette-0.2-0 \
    libenchant-2-2 \
    libsecret-1-0 \
    libgles2-mesa

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
