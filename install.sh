#!/bin/bash

# Install script for Timing-Notion Sync automation

echo "Installing Timing-Notion Sync automation..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "ERROR: .env file not found!"
    echo "Please create a .env file with:"
    echo "  TIMING_API_TOKEN=your_timing_token"
    echo "  NOTION_API_TOKEN=your_notion_token"
    echo "  NOTION_DATABASE_ID=your_database_id"
    echo "  USERNAME=your_username"
    exit 1
fi

# Load USERNAME from .env
export $(grep USERNAME .env | xargs)

if [ -z "$USERNAME" ]; then
    echo "ERROR: USERNAME not set in .env file!"
    echo "Please add: USERNAME=your_macos_username"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user requests python-dotenv || pip3 install --break-system-packages requests python-dotenv || echo "Note: Please ensure 'requests' and 'python-dotenv' are installed"

# Create logs directory
mkdir -p logs

# Generate plist from template
echo "Generating launchd configuration for user: $USERNAME..."
sed "s/{USERNAME}/$USERNAME/g" com.timing-notion-sync.plist.template > com.timing-notion-sync.plist

# Copy launchd plist to user LaunchAgents
echo "Installing launchd service..."
cp com.timing-notion-sync.plist ~/Library/LaunchAgents/

# Load the service
echo "Starting service..."
launchctl load ~/Library/LaunchAgents/com.timing-notion-sync.plist

echo "Installation complete!"
echo ""
echo "The sync will run every 15 minutes."
echo "To check status: launchctl list | grep timing-notion-sync"
echo "To stop: launchctl unload ~/Library/LaunchAgents/com.timing-notion-sync.plist"
echo "To start: launchctl load ~/Library/LaunchAgents/com.timing-notion-sync.plist"
echo ""
echo "Error logs will be in: logs/error.log"
echo "Desktop notifications will appear on sync errors"