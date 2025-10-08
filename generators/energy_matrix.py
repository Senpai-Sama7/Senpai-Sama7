#!/usr/bin/env python3
"""
Generate an energy matrix heat block showing language usage intensity.
"""
import os
import requests
from datetime import datetime, timedelta

def fetch_language_stats(username, token=None):
    """Fetch language statistics from GitHub."""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        # Get user's repositories
        url = f"https://api.github.com/users/{username}/repos?per_page=100"
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            repos = response.json()
            language_bytes = {}
            
            for repo in repos:
                if not repo.get('fork', False):  # Skip forks
                    lang_url = repo['languages_url']
                    lang_response = requests.get(lang_url, headers=headers, timeout=10)
                    if lang_response.status_code == 200:
                        languages = lang_response.json()
                        for lang, bytes_count in languages.items():
                            language_bytes[lang] = language_bytes.get(lang, 0) + bytes_count
            
            # Sort and get top languages
            sorted_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)
            return sorted_langs[:12]  # Top 12 languages
        else:
            print(f"Warning: API returned status {response.status_code}")
            return generate_sample_languages()
    except Exception as e:
        print(f"Error fetching language data: {e}")
        return generate_sample_languages()

def generate_sample_languages():
    """Generate sample language data."""
    return [
        ("Python", 45000),
        ("JavaScript", 38000),
        ("TypeScript", 32000),
        ("HTML", 28000),
        ("CSS", 22000),
        ("Shell", 15000),
        ("Go", 12000),
        ("Rust", 8000),
    ]

def create_energy_matrix_svg(language_data, width=600, height=200):
    """Create an energy matrix visualization."""
    if not language_data:
        language_data = generate_sample_languages()
    
    # Calculate total and percentages
    total = sum(count for _, count in language_data)
    if total == 0:
        total = 1
    
    # Define colors for different languages
    lang_colors = {
        "Python": "#3776ab",
        "JavaScript": "#f7df1e",
        "TypeScript": "#3178c6",
        "Java": "#007396",
        "C++": "#00599c",
        "C": "#555555",
        "C#": "#239120",
        "Go": "#00add8",
        "Rust": "#ce422b",
        "Ruby": "#cc342d",
        "PHP": "#777bb4",
        "Swift": "#ffac45",
        "Kotlin": "#7f52ff",
        "HTML": "#e34c26",
        "CSS": "#1572b6",
        "Shell": "#89e051",
        "Dart": "#00b4ab",
    }
    
    # Create blocks
    blocks = []
    col_width = 60
    row_height = 40
    margin = 8
    cols = 4
    
    for i, (lang, count) in enumerate(language_data):
        percentage = (count / total) * 100
        intensity = min(percentage / 10, 1.0)  # Normalize to 0-1
        
        row = i // cols
        col = i % cols
        x = col * (col_width + margin) + 10
        y = row * (row_height + margin) + 10
        
        base_color = lang_colors.get(lang, "#667eea")
        
        blocks.append(f'''
  <g>
    <rect x="{x}" y="{y}" width="{col_width}" height="{row_height}" 
          fill="{base_color}" opacity="{0.3 + intensity * 0.7}" 
          rx="4"/>
    <text x="{x + col_width/2}" y="{y + 18}" 
          fill="white" font-size="11" font-weight="600" 
          text-anchor="middle">{lang}</text>
    <text x="{x + col_width/2}" y="{y + 32}" 
          fill="rgba(255,255,255,0.8)" font-size="9" 
          text-anchor="middle">{percentage:.1f}%</text>
  </g>''')
    
    svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <filter id="matrixGlow">
      <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>
  
  <rect width="{width}" height="{height}" fill="rgba(0,0,0,0.2)" rx="8"/>
  
  {''.join(blocks)}
</svg>'''
    
    return svg

def main():
    username = os.environ.get('GITHUB_REPOSITORY_OWNER', 'Senpai-Sama7')
    token = os.environ.get('GITHUB_TOKEN')
    
    print(f"Generating energy matrix for {username}...")
    language_data = fetch_language_stats(username, token)
    svg = create_energy_matrix_svg(language_data)
    
    output_path = 'assets/energy_matrix.svg'
    os.makedirs('assets', exist_ok=True)
    
    with open(output_path, 'w') as f:
        f.write(svg)
    
    print(f"Energy matrix saved to {output_path}")

if __name__ == '__main__':
    main()
