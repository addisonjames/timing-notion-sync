#!/bin/bash

# Uninstall script for Timing-Notion Sync automation

echo "Uninstalling Timing-Notion Sync automation..."

# Unload the service
echo "Stopping service..."
launchctl unload ~/Library/LaunchAgents/com.timing-notion-sync.plist 2>/dev/null

# Remove the plist
echo "Removing launchd service..."
rm -f ~/Library/LaunchAgents/com.timing-notion-sync.plist

echo "Uninstallation complete!"
echo ""
echo "Note: Your script files, logs, and .env file have been preserved."
echo "To completely remove, delete the timing-notion-sync directory."