# ⏱️ Timing to Notion Sync

Automatically sync your daily time tracking data from Timing.app to a Notion database for visualization and reporting. Perfect for creating daily/weekly/monthly time tracking charts and reports in Notion. 

## ✨ Features

- 🔄 Automatic sync every 15 minutes (at :00, :15, :30, :45)
- 📊 Groups time by project with full hierarchy support
- 🕐 Timezone-aware date handling
- 🔐 Secure token storage via environment variables

## 📋 Prerequisites

- macOS (uses launchd for scheduling)
- Python 3 (system Python is fine)
- [Timing.app](https://timingapp.com) Pro account (for API access)
- Notion account with API access

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/timing-notion-sync.git
   cd timing-notion-sync
   ```

2. **Create your environment file**
   ```bash
   cp .env.example .env
   ```

3. **Get your API tokens**
   
   **Timing API Token:**
   - Open Timing.app → Preferences → Web API
   - Enable API and copy your token
   
   **Notion API Token:**
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Create a new integration
   - Copy the Internal Integration Token
   
   **Notion Database ID:**
   - Create a new Notion database or use existing
   - Share it with your integration
   - Copy the database ID from the URL: `notion.so/yourworkspace/[DATABASE_ID]?v=...`

4. **Configure your tokens**
   
   Edit the `.env` file and add your tokens:
   ```
   TIMING_API_TOKEN=your_timing_token_here
   NOTION_API_TOKEN=your_notion_token_here  
   NOTION_DATABASE_ID=your_database_id_here
   USERNAME=your_macos_username_here
   ```

5. **Set up your Notion database**
   
   Required properties (exact names):
   - `Project` (Title) - The project name
   - `Date` (Date) - The date of the time entry
   - `Duration` (Text) - Time in H:MM:SS format
   - `Hours` (Number) - Decimal hours for calculations
   - `Last Sync` (Date) - Timestamp of when the entry was last synced
   
   Optional formula property for readable time:
   - `Readable Time` (Formula) - Converts hours to "Xh Ym Zs" format:
   ```
   format(floor(prop("Hours") * 3600 / 3600)) + "h " +
   format(floor(mod(prop("Hours") * 3600, 3600) / 60)) + "m " +
   format(floor(mod(prop("Hours") * 3600, 60))) + "s"
   ``` 

6. **Install and start the sync**
   ```bash
   ./install.sh
   ```
   
   **Note:** When you see commands in code blocks like above, copy only the command itself (e.g., `./install.sh`), not the ```bash``` markers. Those are just formatting to show it's a terminal command.

## 🔧 Configuration

### Creating Charts in Notion
- Add a Chart view to your database
- Set visualization to show by `Project`
- Set each slice to `Hours` → `Values`

### Sync Frequency
By default, syncs run at :00, :15, :30, and :45 of every hour. To modify:
1. Edit `com.timing-notion-sync.plist`
2. Adjust the `StartCalendarInterval` entries
3. Reload: `launchctl unload ~/Library/LaunchAgents/com.timing-notion-sync.plist && launchctl load ~/Library/LaunchAgents/com.timing-notion-sync.plist`

### Project Grouping
The sync automatically:
- Groups all time entries by project
- Preserves full project hierarchy (e.g., "Work > Client A > Project X")
- Sums durations for each project per day
- Updates existing entries or creates new ones

## 📊 Usage

### Check sync status
```bash
launchctl list | grep timing-notion-sync
```
- Exit code `0` = running successfully
- Exit code `1` = error occurred

### View recent syncs
```bash
tail -20 logs/sync.log
```

### Manual sync
```bash
python3 timing-notion-sync.py
```

**Note:** If you get a "No module named 'dotenv'" error, install the dependencies:

For most users:
```bash
pip3 install --user requests python-dotenv
```

For macOS with Homebrew Python (if you get "externally-managed-environment" error):
```bash
pip3 install --user --break-system-packages requests python-dotenv
```

### Stop syncing
```bash
./uninstall.sh
```

## 🚨 Troubleshooting

### Common Issues

**"No module named requests" error**
- Your Python environment is missing dependencies
- Run: `pip3 install --user requests python-dotenv`

**No data syncing**
- Verify Timing.app has data for today
- Check timezone settings (script uses PDT)
- Ensure API tokens are valid

### Error Handling
When sync fails:
- Error file created on Desktop: `TIMING_SYNC_ERROR_[timestamp].txt`
- Detailed error logged in `logs/error.log`
- Sync continues running on schedule

### Debug Mode
Run manually to see detailed output:
```bash
python3 timing-notion-sync.py
```

## 🔐 Security

- **Never commit `.env` file** - it contains sensitive API tokens
- API tokens are stored locally in `.env` file
- Consider rotating tokens periodically
- The `.gitignore` file excludes sensitive data

## 📁 File Structure

```
timing-notion-sync/
├── timing-notion-sync.py    # Main sync script
├── com.timing-notion-sync.plist  # launchd configuration
├── install.sh              # Installation script
├── uninstall.sh           # Uninstall script
├── .env.example           # Template for API tokens
├── .gitignore            # Excludes sensitive files
├── logs/                 # Error logs (auto-created)
└── README.md            # This file
```

## 🤝 Contributing

Feel free to open issues or submit pull requests. Please ensure you don't commit any personal API tokens or data.

## 👨‍💻 Developer Notes

If you're developing this tool with a virtual environment:

### Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests python-dotenv
```

### Running manually
```bash
# From project directory
.venv/bin/python3 timing-notion-sync.py

# Or activate venv first
source .venv/bin/activate
python3 timing-notion-sync.py
```

### Testing after changes
```bash
# Reload launchd service to test automation
launchctl unload ~/Library/LaunchAgents/com.timing-notion-sync.plist
launchctl load ~/Library/LaunchAgents/com.timing-notion-sync.plist
```

**Note:** The launchd service uses system Python, not your venv. To test with your venv, run manually.

## 📄 License

MIT License - feel free to use and modify as needed.