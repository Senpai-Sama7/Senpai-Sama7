# Profile Asset Generators

This directory contains Python scripts for generating custom SVG visualizations for the GitHub profile README.

## Scripts

### 1. `activity_sparkline.py`
Generates a sparkline chart showing activity trends over the last 30 days.

**Output:** `assets/activity_sparkline.svg`

**Features:**
- Fetches recent GitHub events
- Creates animated gradient sparkline
- Includes glow effects

### 2. `radial_skills.py`
Creates a radial/spider chart displaying technology proficiency levels.

**Output:** `assets/skills_chart.svg`

**Features:**
- Customizable skill list
- 8-axis radar chart
- Gradient fill with glow effects
- Background grid rings

**Customization:**
Edit the `skills` list in the `main()` function:
```python
skills = [
    ("Python", 90),
    ("JavaScript", 85),
    # Add more skills...
]
```

### 3. `energy_matrix.py`
Generates a heat map visualization of language usage across repositories.

**Output:** `assets/energy_matrix.svg`

**Features:**
- Fetches language statistics from GitHub
- Creates colored blocks with intensity-based opacity
- Shows percentage breakdown
- Language-specific color coding

## Usage

### Manual Generation

```bash
# Install dependencies
pip install -r requirements.txt

# Generate all assets
python activity_sparkline.py
python radial_skills.py
python energy_matrix.py
```

### Automatic Generation

The assets are automatically regenerated daily via GitHub Actions (see `.github/workflows/generate-assets.yml`).

## Environment Variables

- `GITHUB_TOKEN`: GitHub API token for authenticated requests (optional but recommended)
- `GITHUB_REPOSITORY_OWNER`: GitHub username (defaults to 'Senpai-Sama7')

## Dependencies

- `requests`: For GitHub API calls

## Rate Limits

The generators use the GitHub API and are subject to rate limits:
- **Unauthenticated:** 60 requests/hour
- **Authenticated:** 5,000 requests/hour

Provide a `GITHUB_TOKEN` to use authenticated requests.

## Customization Guide

### Modifying Colors

Edit the gradient colors in each script:

```python
# Example from activity_sparkline.py
<stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
<stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
```

### Adjusting Dimensions

Change the `width` and `height` parameters:

```python
svg = create_sparkline_svg(data, width=300, height=60)
```

### Adding New Skills

In `radial_skills.py`, add entries to the skills list:

```python
skills = [
    ("Your Skill", 85),  # Value from 0-100
    # ...
]
```

## Troubleshooting

**Issue:** API rate limit exceeded
**Solution:** Provide a GitHub token via `GITHUB_TOKEN` environment variable

**Issue:** Empty or missing data
**Solution:** Generators will fall back to sample data for demonstration

**Issue:** SVG not displaying
**Solution:** Check file paths and ensure assets are committed to the repository
