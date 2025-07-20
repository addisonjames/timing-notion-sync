#!/usr/bin/env python3
"""
Sync Timing.app data to Notion database
Runs to sync today's project time tracking data only
"""

import requests
from datetime import datetime
import os
import sys
from dotenv import load_dotenv
import traceback
import json
from collections import deque
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Configuration
TIMING_API_TOKEN = os.environ.get('TIMING_API_TOKEN')
NOTION_API_TOKEN = os.environ.get('NOTION_API_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

# Error logging configuration
LOG_DIR = Path(__file__).parent / 'logs'
LOG_DIR.mkdir(exist_ok=True)
ERROR_LOG_FILE = LOG_DIR / 'error.log'
MAX_ERROR_ENTRIES = 50


def create_error_file(error_details):
    """Create error file on Desktop with timestamp"""
    timestamp = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    error_file = Path.home() / 'Desktop' / f'TIMING_SYNC_ERROR_{timestamp}.txt'
    
    try:
        with open(error_file, 'w') as f:
            f.write(f"Timing Sync Failed at {datetime.now()}\n\n")
            f.write(f"Error Details:\n{error_details}\n\n")
            f.write("Environment Variables Set:\n")
            f.write(f"TIMING_API_TOKEN: {'Set' if TIMING_API_TOKEN else 'Not Set'}\n")
            f.write(f"NOTION_API_TOKEN: {'Set' if NOTION_API_TOKEN else 'Not Set'}\n")
            f.write(f"NOTION_DATABASE_ID: {'Set' if NOTION_DATABASE_ID else 'Not Set'}\n")
    except Exception as e:
        print(f"Failed to create error file: {e}")

def log_error(error_message):
    """Log error to file, keeping only last MAX_ERROR_ENTRIES"""
    try:
        # Read existing errors
        errors = deque(maxlen=MAX_ERROR_ENTRIES)
        if ERROR_LOG_FILE.exists():
            with open(ERROR_LOG_FILE, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        errors.append(line)
        
        # Add new error
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        errors.append(f"{timestamp} - ERROR: {error_message}")
        
        # Write back
        with open(ERROR_LOG_FILE, 'w') as f:
            for error in errors:
                f.write(error + '\n')
    except Exception as e:
        print(f"Failed to log error: {e}")

def handle_error(error_message, error_details=None):
    """Handle errors with notifications, file creation, and logging"""
    print(f"ERROR: {error_message}")
    if error_details:
        print(f"Details: {error_details}")
    
    # Log the error
    log_error(error_message)
    
    # Create desktop error file
    full_details = f"{error_message}\n\n{error_details if error_details else 'No additional details'}\n\n{traceback.format_exc()}"
    create_error_file(full_details)

# Validate tokens exist
if not TIMING_API_TOKEN or not NOTION_API_TOKEN or not NOTION_DATABASE_ID:
    error_msg = "Please set TIMING_API_TOKEN, NOTION_API_TOKEN, and NOTION_DATABASE_ID environment variables"
    handle_error(error_msg)
    sys.exit(1)

def seconds_to_duration_string(seconds):
    """Convert seconds to H:MM:SS format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"

def get_project_names():
    """Fetch all projects to map IDs to names"""
    url = "https://web.timingapp.com/api/v1/projects"
    headers = {
        'Authorization': f'Bearer {TIMING_API_TOKEN}',
        'Accept': 'application/json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Create a mapping of project ID to name
        project_map = {}
        if 'data' in data:
            for project in data['data']:
                project_id = project.get('self', '').split('/')[-1]
                project_name = project.get('title', 'Unknown')
                if project_id:
                    project_map[project_id] = project_name
        
        return project_map
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch Timing projects: {str(e)}"
        handle_error(error_msg, f"API URL: {url}\nStatus Code: {response.status_code if 'response' in locals() else 'N/A'}")
        raise

def get_timing_data():
    """Fetch today's data from Timing API"""
    # Get today's date in local timezone (PDT)
    today = datetime.now().strftime('%Y-%m-%d')
    
    # Try midnight to midnight in local time
    start_time = f"{today}T00:00:00-07:00"  # PDT offset
    end_time = f"{today}T23:59:59-07:00"
    
    print(f"Fetching data for {today} (PDT)")
    
    url = "https://web.timingapp.com/api/v1/report"
    headers = {
        'Authorization': f'Bearer {TIMING_API_TOKEN}',
        'Accept': 'application/json'
    }
    params = {
        'start_date_min': start_time,
        'start_date_max': end_time,
        'project_grouping_level': -1,  # All projects at any depth
        'include_project_data': 'true'  # Include full project info
    }
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        print(f"API returned {len(data.get('data', []))} entries for {today}")
        
        
        return data
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to fetch Timing data: {str(e)}"
        details = f"API URL: {url}\nDate Range: {start_time} to {end_time}\nStatus Code: {response.status_code if 'response' in locals() else 'N/A'}"
        handle_error(error_msg, details)
        raise

def find_notion_page(date, project):
    """Find existing Notion page with matching date and project"""
    url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"
    headers = {
        'Authorization': f'Bearer {NOTION_API_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    data = {
        "filter": {
            "and": [
                {"property": "Date", "date": {"equals": date}},
                {"property": "Project", "title": {"equals": project}}
            ]
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        results = response.json()['results']
        return results[0]['id'] if results else None
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to query Notion database: {str(e)}"
        details = f"Database ID: {NOTION_DATABASE_ID}\nDate: {date}\nProject: {project}\nStatus Code: {response.status_code if 'response' in locals() else 'N/A'}"
        handle_error(error_msg, details)
        raise

def update_or_create_notion_page(page_id, date, duration_seconds, project):
    """Update existing page or create new one in Notion"""
    headers = {
        'Authorization': f'Bearer {NOTION_API_TOKEN}',
        'Notion-Version': '2022-06-28',
        'Content-Type': 'application/json'
    }
    
    # Convert duration
    duration_string = seconds_to_duration_string(duration_seconds)
    duration_hours = round(duration_seconds / 3600, 3)
    
    properties = {
        "Date": {"date": {"start": date}},
        "Project": {"title": [{"text": {"content": project}}]},
        "Duration": {"rich_text": [{"text": {"content": duration_string}}]},
        "Hours": {"number": duration_hours},
        "Last Sync": {"date": {"start": datetime.now().strftime('%Y-%m-%dT%H:%M:%S-07:00')}}
    }
    
    if page_id:
        # Update existing page
        url = f"https://api.notion.com/v1/pages/{page_id}"
        data = {"properties": properties}
        method = 'PATCH'
    else:
        # Create new page
        url = "https://api.notion.com/v1/pages"
        data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": properties
        }
        method = 'POST'
    
    try:
        response = requests.request(method, url, headers=headers, json=data)
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to {'update' if page_id else 'create'} Notion page: {str(e)}"
        details = f"Project: {project}\nDate: {date}\nDuration: {duration_string}\nResponse: {response.text if 'response' in locals() else 'No response'}"
        handle_error(error_msg, details)
        raise

def main():
    """Main sync function"""
    print(f"Starting Timing to Notion sync at {datetime.now()}")
    
    # Check if user is idle (5 minutes = 300 seconds)
    try:
        idle_time = int(os.popen('ioreg -c IOHIDSystem | grep HIDIdleTime').read().split('=')[1]) / 1000000000
        if idle_time > 300:
            print(f"Computer idle for {idle_time:.0f} seconds, skipping sync")
            sys.exit(0)
    except:
        # If we can't check idle time, continue with sync
        pass
    
    try:
        # Get data from Timing
        timing_data = get_timing_data()
        if not timing_data or 'data' not in timing_data:
            error_msg = "No data received from Timing API"
            handle_error(error_msg)
            return
        
        today = datetime.now().strftime('%Y-%m-%d')
        updated_count = 0
        created_count = 0
        
        # Group entries by project and sum durations
        project_totals = {}
        
        for entry in timing_data['data']:
            # Handle project - get the full project path to avoid naming conflicts
            project_data = entry.get('project')
            if project_data is None:
                project = 'Uncategorized'
                project_id = 'uncategorized'
            elif isinstance(project_data, dict):
                # Use the full title_chain to create unique project names
                title_chain = project_data.get('title_chain', [])
                if title_chain:
                    # Join the full path with " > " separator for clarity
                    project = " > ".join(title_chain)
                else:
                    project = project_data.get('title', 'Unknown')
                project_id = project_data.get('self', 'unknown')
            elif isinstance(project_data, str):
                project = project_data
                project_id = project_data
            else:
                project = 'Uncategorized'
                project_id = 'uncategorized'
                
            duration = entry.get('duration', 0)
            
            # Skip entries with no duration
            if duration < 0:
                continue
            
            # Group by project ID and sum durations
            if project_id not in project_totals:
                project_totals[project_id] = {
                    'project_name': project,
                    'total_duration': 0
                }
            project_totals[project_id]['total_duration'] += duration
            
            # Print individual entries for debugging
            entry_title = entry.get('title', 'No title')
            print(f"  Entry: {project} - {entry_title} - {seconds_to_duration_string(duration)}")
    
        print(f"\nGrouped by project:")
        
        # Process each grouped project
        for project_id, project_info in project_totals.items():
            project_name = project_info['project_name']
            total_duration = project_info['total_duration']
            
            print(f"  {project_name}: {seconds_to_duration_string(total_duration)}")
            
            try:
                # Check if entry exists
                page_id = find_notion_page(today, project_name)
                
                # Update or create
                update_or_create_notion_page(page_id, today, total_duration, project_name)
                
                if page_id:
                    updated_count += 1
                    print(f"Updated: {project_name} - {seconds_to_duration_string(total_duration)}")
                else:
                    created_count += 1
                    print(f"Created: {project_name} - {seconds_to_duration_string(total_duration)}")
            except Exception as e:
                # Log individual project failure but continue with others
                print(f"Failed to sync project {project_name}: {e}")
                continue
    
        # Calculate total time
        total_seconds = sum(info['total_duration'] for info in project_totals.values())
        total_hours = total_seconds / 3600
    
        print(f"\nSync complete: {updated_count} updated, {created_count} created")
        print(f"Total time tracked today: {seconds_to_duration_string(total_seconds)} ({total_hours:.2f} hours)")
        
    except Exception as e:
        error_msg = f"Sync failed: {str(e)}"
        handle_error(error_msg, traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()