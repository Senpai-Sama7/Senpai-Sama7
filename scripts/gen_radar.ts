#!/usr/bin/env node
/**
 * GitHub Skills Radar Chart Generator
 * 
 * A production-ready TypeScript script for generating SVG radar charts from skills data.
 * Includes comprehensive error handling, logging, input validation, and configuration management.
 */

import * as fs from 'fs';
import * as path from 'path';
import { performance } from 'perf_hooks';

// Type definitions
interface Skill {
    name: string;
    level: number;
    category?: string;
}

interface RadarConfig {
    size: number;
    centerRadius: number;
    maxRadius: number;
    gridLevels: number[];
    strokeWidth: number;
    fontSize: number;
    colors: {
        grid: string;
        fill: string;
        stroke: string;
        text: string;
        gradientStart: string;
        gradientEnd: string;
    };
    opacity: {
        fill: number;
        grid: number;
    };
}

interface Point {
    x: number;
    y: number;
}

// Custom error classes
class RadarGeneratorError extends Error {
    constructor(message: string, public readonly code: string) {
        super(message);
        this.name = 'RadarGeneratorError';
    }
}

class ValidationError extends RadarGeneratorError {
    constructor(message: string) {
        super(message, 'VALIDATION_ERROR');
    }
}

// Logger utility
class Logger {
    private static instance: Logger;
    private logLevel: string;

    private constructor() {
        this.logLevel = process.env.LOG_LEVEL || 'INFO';
    }

    static getInstance(): Logger {
        if (!Logger.instance) {
            Logger.instance = new Logger();
        }
        return Logger.instance;
    }

    private shouldLog(level: string): boolean {
        const levels = ['DEBUG', 'INFO', 'WARN', 'ERROR'];
        return levels.indexOf(level) >= levels.indexOf(this.logLevel);
    }

    private formatMessage(level: string, message: string): string {
        const timestamp = new Date().toISOString();
        return `${timestamp} [${level}] ${message}`;
    }

    debug(message: string): void {
        if (this.shouldLog('DEBUG')) {
            console.debug(this.formatMessage('DEBUG', message));
        }
    }

    info(message: string): void {
        if (this.shouldLog('INFO')) {
            console.info(this.formatMessage('INFO', message));
        }
    }

    warn(message: string): void {
        if (this.shouldLog('WARN')) {
            console.warn(this.formatMessage('WARN', message));
        }
    }

    error(message: string): void {
        if (this.shouldLog('ERROR')) {
            console.error(this.formatMessage('ERROR', message));
        }
    }
}

// Configuration manager
class ConfigManager {
    private static defaultConfig: RadarConfig = {
        size: 200,
        centerRadius: 0,
        maxRadius: 70,
        gridLevels: [20, 40, 60, 80, 100],
        strokeWidth: 2,
        fontSize: 10,
        colors: {
            grid: '#e1e5e9',
            fill: 'url(#radarGradient)',
            stroke: '#4facfe',
            text: '#586069',
            gradientStart: '#4facfe',
            gradientEnd: '#00f2fe'
        },
        opacity: {
            fill: 0.6,
            grid: 0.5
        }
    };

    static getConfig(overrides: Partial<RadarConfig> = {}): RadarConfig {
        return {
            ...ConfigManager.defaultConfig,
            ...overrides,
            colors: {
                ...ConfigManager.defaultConfig.colors,
                ...(overrides.colors || {})
            },
            opacity: {
                ...ConfigManager.defaultConfig.opacity,
                ...(overrides.opacity || {})
            }
        };
    }

    static loadConfigFromFile(filePath: string): RadarConfig {
        try {
            if (fs.existsSync(filePath)) {
                const configData = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
                return ConfigManager.getConfig(configData);
            }
        } catch (error) {
            Logger.getInstance().warn(`Failed to load config from ${filePath}: ${error}`);
        }
        return ConfigManager.getConfig();
    }
}

// Input validator
class SkillValidator {
    static validateSkills(skills: any[]): Skill[] {
        if (!Array.isArray(skills)) {
            throw new ValidationError('Skills must be an array');
        }

        if (skills.length === 0) {
            throw new ValidationError('Skills array cannot be empty');
        }

        if (skills.length > 20) {
            throw new ValidationError('Too many skills (maximum 20 allowed)');
        }

        return skills.map((skill, index) => {
            if (typeof skill !== 'object' || skill === null) {
                throw new ValidationError(`Skill at index ${index} must be an object`);
            }

            if (typeof skill.name !== 'string' || skill.name.trim().length === 0) {
                throw new ValidationError(`Skill at index ${index} must have a valid name`);
            }

            if (typeof skill.level !== 'number' || skill.level < 0 || skill.level > 100) {
                throw new ValidationError(`Skill at index ${index} must have a level between 0 and 100`);
            }

            return {
                name: skill.name.trim(),
                level: Math.round(skill.level),
                category: skill.category || 'general'
            };
        });
    }
}

// Main radar chart generator
class RadarChartGenerator {
    private config: RadarConfig;
    private logger: Logger;

    constructor(config: RadarConfig) {
        this.config = config;
        this.logger = Logger.getInstance();
    }

    generateRadarChart(skills: Skill[]): string {
        const startTime = performance.now();
        
        try {
            this.logger.info(`Generating radar chart for ${skills.length} skills`);
            
            const validatedSkills = SkillValidator.validateSkills(skills);
            const center = this.config.size / 2;
            
            // Generate chart components
            const gridCircles = this.generateGridCircles(center);
            const gridLines = this.generateGridLines(center, validatedSkills.length);
            const dataPolygon = this.generateDataPolygon(center, validatedSkills);
            const labels = this.generateLabels(center, validatedSkills);
            const gradient = this.generateGradient();
            
            // Assemble SVG
            const svg = this.assembleSVG(gridCircles, gridLines, dataPolygon, labels, gradient);
            
            const endTime = performance.now();
            this.logger.info(`Radar chart generated successfully in ${(endTime - startTime).toFixed(2)}ms`);
            
            return svg;
            
        } catch (error) {
            this.logger.error(`Radar chart generation failed: ${error}`);
            throw error;
        }
    }

    private generateGridCircles(center: number): string {
        return this.config.gridLevels
            .map(level => {
                const radius = this.config.maxRadius * (level / 100);
                return `<circle cx="${center}" cy="${center}" r="${radius}" fill="none" stroke="${this.config.colors.grid}" stroke-width="1" opacity="${this.config.opacity.grid}"/>`;
            })
            .join('\n  ');
    }

    private generateGridLines(center: number, numSkills: number): string {
        const lines: string[] = [];
        
        for (let i = 0; i < numSkills; i++) {
            const angle = (i * 2 * Math.PI) / numSkills - Math.PI / 2;
            const endX = center + Math.cos(angle) * this.config.maxRadius;
            const endY = center + Math.sin(angle) * this.config.maxRadius;
            
            lines.push(`<line x1="${center}" y1="${center}" x2="${endX.toFixed(2)}" y2="${endY.toFixed(2)}" stroke="${this.config.colors.grid}" stroke-width="1" opacity="${this.config.opacity.grid}"/>`);
        }
        
        return lines.join('\n  ');
    }

    private generateDataPolygon(center: number, skills: Skill[]): string {
        const points = skills.map((skill, i) => {
            const angle = (i * 2 * Math.PI) / skills.length - Math.PI / 2;
            const radius = this.config.maxRadius * (skill.level / 100);
            const x = center + Math.cos(angle) * radius;
            const y = center + Math.sin(angle) * radius;
            return `${x.toFixed(2)},${y.toFixed(2)}`;
        }).join(' ');

        return `<polygon points="${points}" fill="${this.config.colors.fill}" stroke="${this.config.colors.stroke}" stroke-width="${this.config.strokeWidth}" opacity="${this.config.opacity.fill}"/>`;
    }

    private generateLabels(center: number, skills: Skill[]): string {
        return skills.map((skill, i) => {
            const angle = (i * 2 * Math.PI) / skills.length - Math.PI / 2;
            const labelRadius = this.config.maxRadius * 1.2;
            const x = center + Math.cos(angle) * labelRadius;
            const y = center + Math.sin(angle) * labelRadius;
            
            // Adjust text anchor based on position
            let textAnchor = 'middle';
            if (x < center - 10) textAnchor = 'end';
            else if (x > center + 10) textAnchor = 'start';
            
            return `<text x="${x.toFixed(2)}" y="${y.toFixed(2)}" text-anchor="${textAnchor}" dominant-baseline="middle" font-family="Arial, sans-serif" font-size="${this.config.fontSize}" fill="${this.config.colors.text}">${this.escapeXML(skill.name)}</text>`;
        }).join('\n  ');
    }

    private generateGradient(): string {
        return `<linearGradient id="radarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:${this.config.colors.gradientStart};stop-opacity:${this.config.opacity.fill}"/>
      <stop offset="100%" style="stop-color:${this.config.colors.gradientEnd};stop-opacity:${this.config.opacity.fill * 0.5}"/>
    </linearGradient>`;
    }

    private assembleSVG(gridCircles: string, gridLines: string, dataPolygon: string, labels: string, gradient: string): string {
        return `<svg width="${this.config.size}" height="${this.config.size}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Skills radar chart">
  <title>Skills Radar Chart</title>
  <desc>Visualization of technical skills and proficiency levels</desc>
  <defs>
    ${gradient}
  </defs>
  ${gridCircles}
  ${gridLines}
  ${dataPolygon}
  ${labels}
</svg>`;
    }

    private escapeXML(text: string): string {
        return text
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }
}

// CLI argument parser
interface CLIArgs {
    input?: string;
    output?: string;
    config?: string;
    size?: number;
    logLevel?: string;
    help?: boolean;
    useSampleData?: boolean;
}

class ArgumentParser {
    static parse(args: string[]): CLIArgs {
        const parsed: CLIArgs = {};
        
        for (let i = 0; i < args.length; i++) {
            const arg = args[i];
            
            switch (arg) {
                case '--help':
                case '-h':
                    parsed.help = true;
                    break;
                case '--input':
                case '-i':
                    parsed.input = args[++i];
                    break;
                case '--output':
                case '-o':
                    parsed.output = args[++i];
                    break;
                case '--config':
                case '-c':
                    parsed.config = args[++i];
                    break;
                case '--size':
                case '-s':
                    parsed.size = parseInt(args[++i], 10);
                    break;
                case '--log-level':
                case '-l':
                    parsed.logLevel = args[++i];
                    break;
                case '--use-sample-data':
                    parsed.useSampleData = true;
                    break;
            }
        }
        
        return parsed;
    }

    static showHelp(): void {
        console.log(`
GitHub Skills Radar Chart Generator

Usage: node gen_radar.js [options]

Options:
  -h, --help              Show this help message
  -i, --input <file>      Input JSON file with skills data
  -o, --output <file>     Output SVG file (default: stdout)
  -c, --config <file>     Configuration file path
  -s, --size <number>     Chart size in pixels (default: 200)
  -l, --log-level <level> Log level (DEBUG, INFO, WARN, ERROR)
  --use-sample-data       Use built-in sample data

Examples:
  node gen_radar.js --use-sample-data
  node gen_radar.js -i skills.json -o radar.svg
  node gen_radar.js -c config.json --size 300
        `);
    }
}

// Sample data provider
class SampleDataProvider {
    static getSkills(): Skill[] {
        return [
            { name: 'JavaScript', level: 90, category: 'programming' },
            { name: 'Python', level: 85, category: 'programming' },
            { name: 'React', level: 88, category: 'frontend' },
            { name: 'Node.js', level: 82, category: 'backend' },
            { name: 'Docker', level: 75, category: 'devops' },
            { name: 'AWS', level: 70, category: 'cloud' },
            { name: 'TypeScript', level: 85, category: 'programming' },
            { name: 'PostgreSQL', level: 78, category: 'database' }
        ];
    }
}

// Main application
async function main(): Promise<number> {
    try {
        const args = ArgumentParser.parse(process.argv.slice(2));
        
        // Set log level
        if (args.logLevel) {
            process.env.LOG_LEVEL = args.logLevel.toUpperCase();
        }
        
        const logger = Logger.getInstance();
        
        if (args.help) {
            ArgumentParser.showHelp();
            return 0;
        }
        
        logger.info('Starting radar chart generation');
        
        // Load configuration
        const config = args.config 
            ? ConfigManager.loadConfigFromFile(args.config)
            : ConfigManager.getConfig({ size: args.size });
        
        // Load skills data
        let skills: Skill[];
        
        if (args.useSampleData) {
            logger.info('Using sample skills data');
            skills = SampleDataProvider.getSkills();
        } else if (args.input) {
            logger.info(`Loading skills from ${args.input}`);
            const inputData = JSON.parse(fs.readFileSync(args.input, 'utf-8'));
            skills = Array.isArray(inputData) ? inputData : inputData.skills;
        } else {
            logger.info('Using default sample data (no input specified)');
            skills = SampleDataProvider.getSkills();
        }
        
        // Generate radar chart
        const generator = new RadarChartGenerator(config);
        const svg = generator.generateRadarChart(skills);
        
        // Output result
        if (args.output) {
            fs.writeFileSync(args.output, svg, 'utf-8');
            logger.info(`Radar chart saved to ${args.output}`);
        } else {
            console.log(svg);
        }
        
        logger.info('Radar chart generation completed successfully');
        return 0;
        
    } catch (error) {
        const logger = Logger.getInstance();
        
        if (error instanceof ValidationError) {
            logger.error(`Validation error: ${error.message}`);
            return 1;
        } else if (error instanceof RadarGeneratorError) {
            logger.error(`Generator error: ${error.message}`);
            return 1;
        } else {
            logger.error(`Unexpected error: ${error}`);
            return 1;
        }
    }
}

// Handle process signals
process.on('SIGINT', () => {
    Logger.getInstance().info('Operation cancelled by user');
    process.exit(130);
});

process.on('unhandledRejection', (reason, promise) => {
    Logger.getInstance().error(`Unhandled rejection at ${promise}: ${reason}`);
    process.exit(1);
});

// Export for testing
export {
    RadarChartGenerator,
    SkillValidator,
    ConfigManager,
    SampleDataProvider,
    Skill,
    RadarConfig
};

// Run if called directly
if (require.main === module) {
    main().then(process.exit);
}