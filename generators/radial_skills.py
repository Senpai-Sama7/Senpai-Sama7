#!/usr/bin/env python3
"""
Generate a radial skill chart SVG showing technology proficiency levels.
"""
import math

def create_radial_chart(skills, size=400):
    """
    Create a radial/spider chart for skills.
    skills: list of tuples [(name, value), ...] where value is 0-100
    """
    center_x = size / 2
    center_y = size / 2
    max_radius = size / 2.5
    
    num_skills = len(skills)
    angle_step = 2 * math.pi / num_skills
    
    # Calculate points for the skill polygon
    points = []
    for i, (name, value) in enumerate(skills):
        angle = i * angle_step - math.pi / 2  # Start from top
        radius = (value / 100) * max_radius
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    
    # Create polygon path
    polygon_points = " ".join([f"{x:.2f},{y:.2f}" for x, y in points])
    
    # Create background rings
    rings = []
    for level in [0.25, 0.5, 0.75, 1.0]:
        ring_points = []
        for i in range(num_skills):
            angle = i * angle_step - math.pi / 2
            radius = level * max_radius
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            ring_points.append(f"{x:.2f},{y:.2f}")
        rings.append(" ".join(ring_points))
    
    # Create axis lines and labels
    axes = []
    labels = []
    for i, (name, value) in enumerate(skills):
        angle = i * angle_step - math.pi / 2
        end_x = center_x + max_radius * 1.1 * math.cos(angle)
        end_y = center_y + max_radius * 1.1 * math.sin(angle)
        
        axes.append(f'<line x1="{center_x}" y1="{center_y}" x2="{end_x:.2f}" y2="{end_y:.2f}" stroke="rgba(255,255,255,0.15)" stroke-width="1"/>')
        
        # Position labels
        label_x = center_x + max_radius * 1.25 * math.cos(angle)
        label_y = center_y + max_radius * 1.25 * math.sin(angle)
        
        # Adjust text anchor based on position
        if label_x > center_x + 5:
            anchor = "start"
        elif label_x < center_x - 5:
            anchor = "end"
        else:
            anchor = "middle"
        
        labels.append(f'<text x="{label_x:.2f}" y="{label_y:.2f}" fill="rgba(255,255,255,0.9)" font-size="13" font-weight="600" text-anchor="{anchor}" dominant-baseline="middle">{name}</text>')
    
    svg = f'''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="skillGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.6" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:0.8" />
    </linearGradient>
    <filter id="skillGlow">
      <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
      <feMerge>
        <feMergeNode in="coloredBlur"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
    <radialGradient id="bgGradient">
      <stop offset="0%" style="stop-color:rgba(255,255,255,0.05);stop-opacity:1" />
      <stop offset="100%" style="stop-color:rgba(255,255,255,0);stop-opacity:1" />
    </radialGradient>
  </defs>
  
  <!-- Background -->
  <rect width="{size}" height="{size}" fill="transparent"/>
  <circle cx="{center_x}" cy="{center_y}" r="{max_radius}" fill="url(#bgGradient)" opacity="0.3"/>
  
  <!-- Grid rings -->
  {''.join([f'<polygon points="{ring}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1"/>' for ring in rings])}
  
  <!-- Axes -->
  {''.join(axes)}
  
  <!-- Skill polygon -->
  <polygon points="{polygon_points}" fill="url(#skillGradient)" stroke="#667eea" stroke-width="2" filter="url(#skillGlow)"/>
  <polygon points="{polygon_points}" fill="none" stroke="rgba(255,255,255,0.3)" stroke-width="1"/>
  
  <!-- Labels -->
  {''.join(labels)}
</svg>'''
    
    return svg

def main():
    # Define skills - customize these!
    skills = [
        ("Python", 90),
        ("JavaScript", 85),
        ("React", 80),
        ("Node.js", 75),
        ("Docker", 70),
        ("AWS", 65),
        ("PostgreSQL", 85),
        ("Git", 95)
    ]
    
    svg = create_radial_chart(skills, size=400)
    
    output_path = 'assets/skills_chart.svg'
    with open(output_path, 'w') as f:
        f.write(svg)
    
    print(f"Radial skill chart saved to {output_path}")

if __name__ == '__main__':
    main()
