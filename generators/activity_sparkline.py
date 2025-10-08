#!/usr/bin/env python3
"""
Generate an activity sparkline SVG based on recent GitHub activity.
This creates a small line chart showing contribution trends over time.
"""
import os
import json
import requests
from datetime import datetime, timedelta

def fetch_contribution_data(username, token=None):
    """Fetch contribution data from GitHub API."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    # Get events for the user
    url = f"https://api.github.com/users/{username}/events/public"
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            events = response.json()
            # Count events per day for the last 30 days
            daily_counts = {}
            today = datetime.utcnow().date()
            
            for event in events:
                event_date = datetime.strptime(event['created_at'], '%Y-%m-%dT%H:%M:%SZ').date()
                date_key = event_date.isoformat()
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
            
            # Fill in missing days with 0
            result = []
            for i in range(29, -1, -1):
                date = today - timedelta(days=i)
                date_key = date.isoformat()
                result.append(daily_counts.get(date_key, 0))
            
            return result
        else:
            print(f"Warning: API returned status {response.status_code}")
            return generate_sample_data()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data for demonstration."""
    import random
    random.seed(42)
    return [random.randint(0, 20) for _ in range(30)]

def create_sparkline_svg(data, width=300, height=60):
    """Create an SVG sparkline from the data."""
    if not data or max(data) == 0:
        max_val = 1
    else:
        max_val = max(data)
    
    points = []
    step_x = width / (len(data) - 1) if len(data) > 1 else width
    
    for i, value in enumerate(data):
        x = i * step_x
        y = height - (value / max_val * (height - 10)) - 5
        points.append(f"{x:.2f},{y:.2f}")
    
    polyline = " ".join(points)
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sparkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
    <filter id="glow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  <polyline
    fill="none"
    stroke="url(#sparkGradient)"
    stroke-width="2.5"
    points="{polyline}"
    filter="url(#glow)"
  />
  <polyline
    fill="none"
    stroke="rgba(102, 126, 234, 0.2)"
    stroke-width="1"
    points="{polyline}"
    transform="translate(0, 2)"
  />
</svg>'''
    
    return svg

def main():
    username = os.environ.get('GITHUB_REPOSITORY_OWNER', 'Senpai-Sama7')
    token = os.environ.get('GITHUB_TOKEN')
    
    print(f"Generating activity sparkline for {username}...")
    data = fetch_contribution_data(username, token)
    svg = create_sparkline_svg(data)
    
    output_path = 'assets/activity_sparkline.svg'
    os.makedirs('assets', exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(svg)
    
    print(f"Sparkline saved to {output_path}")

if __name__ == '__main__':
    main()
