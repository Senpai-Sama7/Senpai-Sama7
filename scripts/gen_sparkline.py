#!/usr/bin/env python3
"""Generate SVG sparkline from GitHub activity data."""

import json
import sys
from datetime import datetime, timedelta

def generate_sparkline(data_points, width=400, height=60):
    """Generate SVG sparkline from data points."""
    if not data_points:
        return ""
    
    max_val = max(data_points) if max(data_points) > 0 else 1
    points = []
    
    for i, val in enumerate(data_points):
        x = (i / (len(data_points) - 1)) * width
        y = height - (val / max_val) * (height - 10)
        points.append(f"{x},{y}")
    
    polyline = " ".join(points)
    
    return f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sparkGradient" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#4facfe;stop-opacity:0.8"/>
      <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:0.8"/>
    </linearGradient>
  </defs>
  <polyline points="{polyline}" fill="none" stroke="url(#sparkGradient)" stroke-width="2"/>
  <circle cx="{width-5}" cy="{height - (data_points[-1] / max_val) * (height - 10)}" r="3" fill="#00f2fe"/>
</svg>'''

if __name__ == "__main__":
    # Sample data - replace with actual GitHub API data
    sample_data = [12, 15, 8, 23, 18, 25, 30, 22, 19, 28, 35, 20, 15, 18, 25]
    print(generate_sparkline(sample_data))