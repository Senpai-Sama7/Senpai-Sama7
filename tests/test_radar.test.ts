/**
 * Comprehensive test suite for the radar chart generator.
 * Tests all functionality including error handling, edge cases, and integration scenarios.
 */

import * as fs from 'fs';
import * as path from 'path';
import { performance } from 'perf_hooks';

// Import the modules to test
import {
  RadarChartGenerator,
  SkillValidator,
  ConfigManager,
  SampleDataProvider,
  Skill,
  RadarConfig
} from '../scripts/gen_radar';

describe('SkillValidator', () => {
  describe('validateSkills', () => {
    it('should validate correct skills array', () => {
      const skills = [
        { name: 'JavaScript', level: 90 },
        { name: 'Python', level: 85 }
      ];
      
      const result = SkillValidator.validateSkills(skills);
      
      expect(result).toHaveLength(2);
      expect(result[0].name).toBe('JavaScript');
      expect(result[0].level).toBe(90);
      expect(result[0].category).toBe('general');
    });

    it('should throw error for non-array input', () => {
      expect(() => {
        SkillValidator.validateSkills('not an array' as any);
      }).toThrow('Skills must be an array');
    });

    it('should throw error for empty array', () => {
      expect(() => {
        SkillValidator.validateSkills([]);
      }).toThrow('Skills array cannot be empty');
    });

    it('should throw error for too many skills', () => {
      const tooManySkills = Array.from({ length: 21 }, (_, i) => ({
        name: `Skill ${i}`,
        level: 50
      }));
      
      expect(() => {
        SkillValidator.validateSkills(tooManySkills);
      }).toThrow('Too many skills (maximum 20 allowed)');
    });

    it('should throw error for invalid skill object', () => {
      expect(() => {
        SkillValidator.validateSkills([null]);
      }).toThrow('Skill at index 0 must be an object');
    });

    it('should throw error for missing name', () => {
      expect(() => {
        SkillValidator.validateSkills([{ level: 50 }]);
      }).toThrow('Skill at index 0 must have a valid name');
    });

    it('should throw error for empty name', () => {
      expect(() => {
        SkillValidator.validateSkills([{ name: '', level: 50 }]);
      }).toThrow('Skill at index 0 must have a valid name');
    });

    it('should throw error for invalid level', () => {
      expect(() => {
        SkillValidator.validateSkills([{ name: 'Test', level: -1 }]);
      }).toThrow('Skill at index 0 must have a level between 0 and 100');
    });

    it('should throw error for level over 100', () => {
      expect(() => {
        SkillValidator.validateSkills([{ name: 'Test', level: 101 }]);
      }).toThrow('Skill at index 0 must have a level between 0 and 100');
    });

    it('should round decimal levels', () => {
      const skills = [{ name: 'Test', level: 85.7 }];
      const result = SkillValidator.validateSkills(skills);
      
      expect(result[0].level).toBe(86);
    });

    it('should trim skill names', () => {
      const skills = [{ name: '  JavaScript  ', level: 90 }];
      const result = SkillValidator.validateSkills(skills);
      
      expect(result[0].name).toBe('JavaScript');
    });

    it('should preserve custom categories', () => {
      const skills = [{ name: 'React', level: 90, category: 'frontend' }];
      const result = SkillValidator.validateSkills(skills);
      
      expect(result[0].category).toBe('frontend');
    });
  });
});

describe('ConfigManager', () => {
  describe('getConfig', () => {
    it('should return default config when no overrides provided', () => {
      const config = ConfigManager.getConfig();
      
      expect(config.size).toBe(200);
      expect(config.maxRadius).toBe(70);
      expect(config.gridLevels).toEqual([20, 40, 60, 80, 100]);
      expect(config.colors.stroke).toBe('#4facfe');
    });

    it('should merge overrides with defaults', () => {
      const overrides = {
        size: 300,
        colors: { stroke: '#ff0000' }
      };
      
      const config = ConfigManager.getConfig(overrides);
      
      expect(config.size).toBe(300);
      expect(config.colors.stroke).toBe('#ff0000');
      expect(config.maxRadius).toBe(70); // Should keep default
      expect(config.colors.fill).toBe('url(#radarGradient)'); // Should keep default
    });
  });

  describe('loadConfigFromFile', () => {
    const testConfigPath = path.join(__dirname, 'test-config.json');

    afterEach(() => {
      if (fs.existsSync(testConfigPath)) {
        fs.unlinkSync(testConfigPath);
      }
    });

    it('should load config from valid JSON file', () => {
      const testConfig = { size: 400, strokeWidth: 3 };
      fs.writeFileSync(testConfigPath, JSON.stringify(testConfig));
      
      const config = ConfigManager.loadConfigFromFile(testConfigPath);
      
      expect(config.size).toBe(400);
      expect(config.strokeWidth).toBe(3);
    });

    it('should return default config for non-existent file', () => {
      const config = ConfigManager.loadConfigFromFile('non-existent.json');
      
      expect(config.size).toBe(200); // Default value
    });

    it('should return default config for invalid JSON', () => {
      fs.writeFileSync(testConfigPath, 'invalid json');
      
      const config = ConfigManager.loadConfigFromFile(testConfigPath);
      
      expect(config.size).toBe(200); // Default value
    });
  });
});

describe('SampleDataProvider', () => {
  describe('getSkills', () => {
    it('should return valid sample skills', () => {
      const skills = SampleDataProvider.getSkills();
      
      expect(Array.isArray(skills)).toBe(true);
      expect(skills.length).toBeGreaterThan(0);
      
      skills.forEach(skill => {
        expect(typeof skill.name).toBe('string');
        expect(typeof skill.level).toBe('number');
        expect(skill.level).toBeGreaterThanOrEqual(0);
        expect(skill.level).toBeLessThanOrEqual(100);
        expect(typeof skill.category).toBe('string');
      });
    });

    it('should return consistent data', () => {
      const skills1 = SampleDataProvider.getSkills();
      const skills2 = SampleDataProvider.getSkills();
      
      expect(skills1).toEqual(skills2);
    });
  });
});

describe('RadarChartGenerator', () => {
  let generator: RadarChartGenerator;
  let config: RadarConfig;

  beforeEach(() => {
    config = ConfigManager.getConfig();
    generator = new RadarChartGenerator(config);
  });

  describe('generateRadarChart', () => {
    it('should generate valid SVG for sample skills', () => {
      const skills = SampleDataProvider.getSkills();
      const svg = generator.generateRadarChart(skills);
      
      expect(typeof svg).toBe('string');
      expect(svg).toMatch(/^<svg/);
      expect(svg).toMatch(/<\/svg>$/);
      expect(svg).toContain('width="200"');
      expect(svg).toContain('height="200"');
      expect(svg).toContain('radarGradient');
      expect(svg).toContain('polygon');
    });

    it('should include accessibility attributes', () => {
      const skills = [{ name: 'Test', level: 50 }];
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toContain('role="img"');
      expect(svg).toContain('aria-label="Skills radar chart"');
      expect(svg).toContain('<title>');
      expect(svg).toContain('<desc>');
    });

    it('should handle single skill', () => {
      const skills = [{ name: 'JavaScript', level: 90 }];
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toContain('JavaScript');
      expect(svg).toContain('polygon');
    });

    it('should handle maximum skills', () => {
      const skills = Array.from({ length: 20 }, (_, i) => ({
        name: `Skill ${i + 1}`,
        level: 50 + i
      }));
      
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toContain('polygon');
      expect(svg).toContain('Skill 1');
      expect(svg).toContain('Skill 20');
    });

    it('should handle zero-level skills', () => {
      const skills = [
        { name: 'Skill1', level: 0 },
        { name: 'Skill2', level: 50 }
      ];
      
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toContain('polygon');
      expect(svg).toContain('Skill1');
      expect(svg).toContain('Skill2');
    });

    it('should handle all maximum-level skills', () => {
      const skills = [
        { name: 'Skill1', level: 100 },
        { name: 'Skill2', level: 100 }
      ];
      
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toContain('polygon');
    });

    it('should escape XML characters in skill names', () => {
      const skills = [
        { name: 'C++ & Templates', level: 80 },
        { name: 'HTML <tags>', level: 70 }
      ];
      
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toContain('C++ &amp; Templates');
      expect(svg).toContain('HTML &lt;tags&gt;');
    });

    it('should throw error for invalid skills', () => {
      expect(() => {
        generator.generateRadarChart([] as any);
      }).toThrow();
    });

    it('should measure performance', () => {
      const skills = SampleDataProvider.getSkills();
      
      const startTime = performance.now();
      generator.generateRadarChart(skills);
      const endTime = performance.now();
      
      const duration = endTime - startTime;
      expect(duration).toBeLessThan(100); // Should complete in under 100ms
    });
  });

  describe('private methods', () => {
    it('should generate grid circles', () => {
      const gridCircles = (generator as any).generateGridCircles(100);
      
      expect(typeof gridCircles).toBe('string');
      expect(gridCircles).toContain('<circle');
      expect(gridCircles).toContain('cx="100"');
      expect(gridCircles).toContain('cy="100"');
    });

    it('should generate grid lines', () => {
      const gridLines = (generator as any).generateGridLines(100, 6);
      
      expect(typeof gridLines).toBe('string');
      expect(gridLines).toContain('<line');
      expect((gridLines.match(/<line/g) || []).length).toBe(6);
    });

    it('should generate data polygon', () => {
      const skills = [
        { name: 'Skill1', level: 50 },
        { name: 'Skill2', level: 75 }
      ];
      
      const polygon = (generator as any).generateDataPolygon(100, skills);
      
      expect(typeof polygon).toBe('string');
      expect(polygon).toContain('<polygon');
      expect(polygon).toContain('points=');
    });

    it('should generate labels with proper text anchoring', () => {
      const skills = [
        { name: 'Left', level: 50 },
        { name: 'Right', level: 50 },
        { name: 'Center', level: 50 }
      ];
      
      const labels = (generator as any).generateLabels(100, skills);
      
      expect(typeof labels).toBe('string');
      expect(labels).toContain('Left');
      expect(labels).toContain('Right');
      expect(labels).toContain('Center');
      expect(labels).toContain('text-anchor=');
    });

    it('should escape XML characters correctly', () => {
      const escaped = (generator as any).escapeXML('Test & <script>alert("xss")</script>');
      
      expect(escaped).toBe('Test &amp; &lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;');
    });
  });
});

describe('Integration Tests', () => {
  it('should generate complete radar chart end-to-end', () => {
    const skills = [
      { name: 'JavaScript', level: 90, category: 'programming' },
      { name: 'Python', level: 85, category: 'programming' },
      { name: 'React', level: 88, category: 'frontend' },
      { name: 'Node.js', level: 82, category: 'backend' }
    ];
    
    const config = ConfigManager.getConfig({ size: 250 });
    const generator = new RadarChartGenerator(config);
    
    const svg = generator.generateRadarChart(skills);
    
    // Verify structure
    expect(svg).toMatch(/^<svg[^>]*>/);
    expect(svg).toMatch(/<\/svg>$/);
    
    // Verify dimensions
    expect(svg).toContain('width="250"');
    expect(svg).toContain('height="250"');
    
    // Verify content
    expect(svg).toContain('JavaScript');
    expect(svg).toContain('Python');
    expect(svg).toContain('React');
    expect(svg).toContain('Node.js');
    
    // Verify SVG elements
    expect(svg).toContain('<defs>');
    expect(svg).toContain('<polygon');
    expect(svg).toContain('<circle');
    expect(svg).toContain('<text');
    
    // Verify accessibility
    expect(svg).toContain('role="img"');
    expect(svg).toContain('<title>');
    expect(svg).toContain('<desc>');
  });

  it('should handle configuration variations', () => {
    const skills = SampleDataProvider.getSkills();
    
    const configs = [
      { size: 150 },
      { size: 300, strokeWidth: 3 },
      { colors: { stroke: '#ff0000', fill: '#00ff00' } }
    ];
    
    configs.forEach(configOverride => {
      const config = ConfigManager.getConfig(configOverride);
      const generator = new RadarChartGenerator(config);
      const svg = generator.generateRadarChart(skills);
      
      expect(svg).toMatch(/^<svg/);
      expect(svg).toMatch(/<\/svg>$/);
      
      if (configOverride.size) {
        expect(svg).toContain(`width="${configOverride.size}"`);
        expect(svg).toContain(`height="${configOverride.size}"`);
      }
    });
  });

  it('should validate performance requirements', () => {
    const skills = Array.from({ length: 15 }, (_, i) => ({
      name: `Skill ${i + 1}`,
      level: Math.floor(Math.random() * 100)
    }));
    
    const config = ConfigManager.getConfig();
    const generator = new RadarChartGenerator(config);
    
    const iterations = 10;
    const times: number[] = [];
    
    for (let i = 0; i < iterations; i++) {
      const startTime = performance.now();
      generator.generateRadarChart(skills);
      const endTime = performance.now();
      times.push(endTime - startTime);
    }
    
    const averageTime = times.reduce((a, b) => a + b, 0) / times.length;
    const maxTime = Math.max(...times);
    
    expect(averageTime).toBeLessThan(50); // Average under 50ms
    expect(maxTime).toBeLessThan(100); // Max under 100ms
  });
});

describe('Error Handling', () => {
  let generator: RadarChartGenerator;

  beforeEach(() => {
    const config = ConfigManager.getConfig();
    generator = new RadarChartGenerator(config);
  });

  it('should handle validation errors gracefully', () => {
    expect(() => {
      generator.generateRadarChart([]);
    }).toThrow('Skills array cannot be empty');
  });

  it('should handle malformed skill objects', () => {
    expect(() => {
      generator.generateRadarChart([{ name: null, level: 'invalid' }] as any);
    }).toThrow();
  });

  it('should handle extreme values', () => {
    const skills = [
      { name: 'A'.repeat(100), level: 0 },
      { name: 'B', level: 100 }
    ];
    
    expect(() => {
      generator.generateRadarChart(skills);
    }).not.toThrow();
  });
});