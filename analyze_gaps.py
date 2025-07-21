import re
from datetime import datetime

# Read the log file
with open('logs/sync.log', 'r') as f:
    content = f.read()

# Extract all sync timestamps
pattern = r'Starting Timing to Notion sync at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d+)'
matches = re.findall(pattern, content)

# Convert to datetime objects and analyze gaps
if len(matches) > 1:
    timestamps = []
    for match in matches[-30:]:  # Last 30 entries
        dt = datetime.strptime(match.split('.')[0], '%Y-%m-%d %H:%M:%S')
        timestamps.append(dt)
    
    print("Recent sync timing analysis:")
    print("-" * 60)
    
    for i in range(1, len(timestamps)):
        gap = (timestamps[i] - timestamps[i-1]).total_seconds() / 60
        expected_gap = 15  # Expected 15 minute interval
        
        if abs(gap - expected_gap) > 2:  # More than 2 minute deviation
            print(f"{timestamps[i-1].strftime('%Y-%m-%d %H:%M')} -> {timestamps[i].strftime('%H:%M')}")
            print(f"  Gap: {gap:.1f} minutes (expected {expected_gap} minutes)")
            print(f"  Delay: {gap - expected_gap:.1f} minutes")
            print()

