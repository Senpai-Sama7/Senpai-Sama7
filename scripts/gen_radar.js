#!/usr/bin/env node
/**
 * Generate SVG radar chart for skills visualization
 */

function generateRadarChart(skills, size = 200) {
    const center = size / 2;
    const radius = size * 0.35;
    const numSkills = skills.length;
    
    // Generate polygon points
    const points = skills.map((skill, i) => {
        const angle = (i * 2 * Math.PI) / numSkills - Math.PI / 2;
        const x = center + Math.cos(angle) * radius * (skill.level / 100);
        const y = center + Math.sin(angle) * radius * (skill.level / 100);
        return `${x},${y}`;
    }).join(' ');
    
    // Generate grid circles
    const gridCircles = [20, 40, 60, 80, 100].map(percent => 
        `<circle cx="${center}" cy="${center}" r="${radius * (percent / 100)}" 
         fill="none" stroke="#e1e5e9" stroke-width="1" opacity="0.5"/>`
    ).join('\n  ');
    
    // Generate skill labels
    const labels = skills.map((skill, i) => {
        const angle = (i * 2 * Math.PI) / numSkills - Math.PI / 2;
        const labelRadius = radius * 1.15;
        const x = center + Math.cos(angle) * labelRadius;
        const y = center + Math.sin(angle) * labelRadius;
        return `<text x="${x}" y="${y}" text-anchor="middle" dominant-baseline="middle" 
                font-family="Arial, sans-serif" font-size="10" fill="#586069">${skill.name}</text>`;
    }).join('\n  ');
    
    return `<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4facfe;stop-opacity:0.6"/>
      <stop offset="100%" style="stop-color:#00f2fe;stop-opacity:0.3"/>
    </linearGradient>
  </defs>
  ${gridCircles}
  <polygon points="${points}" fill="url(#radarGradient)" stroke="#4facfe" stroke-width="2"/>
  ${labels}
</svg>`;
}

// Sample usage
const sampleSkills = [
    { name: 'JavaScript', level: 90 },
    { name: 'Python', level: 85 },
    { name: 'React', level: 88 },
    { name: 'Node.js', level: 82 },
    { name: 'Docker', level: 75 },
    { name: 'AWS', level: 70 }
];

console.log(generateRadarChart(sampleSkills));