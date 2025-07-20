#!/usr/bin/env python3
import json
from datetime import timedelta

def parse_duration(duration_str):
    """Convert H:MM:SS format to total minutes"""
    parts = duration_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    
    total_minutes = hours * 60 + minutes + seconds / 60
    return total_minutes

def main():
    # Read the JSON data
    with open('logs/timer-export-25-07-17 146pm.json', 'r') as f:
        data = json.load(f)
    
    # Initialize totals
    development_total = 0
    productivity_total = 0
    all_projects_total = 0
    
    # Track all projects for summary
    project_totals = {}
    
    # Process each entry
    for entry in data:
        project = entry['project']
        duration_str = entry['duration']
        duration_minutes = parse_duration(duration_str)
        
        # Add to project totals
        if project not in project_totals:
            project_totals[project] = 0
        project_totals[project] += duration_minutes
        
        # Check for Development project (including sub-projects)
        if project == 'Development' or project == 'Web Browsing ▸ Development':
            development_total += duration_minutes
        
        # Check for Productivity project
        if project == 'Productivity':
            productivity_total += duration_minutes
        
        # Add to overall total
        all_projects_total += duration_minutes
    
    # Print results
    print("=== Timing Export Analysis ===\n")
    
    print("1. Development Project Total:")
    print(f"   - Development: {project_totals.get('Development', 0):.1f} minutes")
    print(f"   - Web Browsing ▸ Development: {project_totals.get('Web Browsing ▸ Development', 0):.1f} minutes")
    print(f"   - TOTAL: {development_total:.1f} minutes ({development_total/60:.1f} hours)\n")
    
    print("2. Productivity Project Total:")
    print(f"   - {productivity_total:.1f} minutes ({productivity_total/60:.1f} hours)\n")
    
    print("3. All Projects Summary:")
    for project, minutes in sorted(project_totals.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {project}: {minutes:.1f} minutes ({minutes/60:.1f} hours)")
    
    print(f"\n4. Grand Total:")
    print(f"   - {all_projects_total:.1f} minutes ({all_projects_total/60:.1f} hours)")
    
    print("\n=== Sync Discrepancy Analysis ===")
    print(f"Export shows {all_projects_total:.1f} minutes total")
    print(f"But only 44 minutes were synced")
    print(f"Missing: {all_projects_total - 44:.1f} minutes ({(all_projects_total - 44)/60:.1f} hours)")
    
    # Show breakdown of each activity
    print("\n=== Detailed Activity Breakdown ===")
    for entry in data:
        duration_minutes = parse_duration(entry['duration'])
        print(f"{entry['application']:20} | {entry['project']:25} | {entry['duration']:8} | {duration_minutes:6.1f} min")

if __name__ == "__main__":
    main()