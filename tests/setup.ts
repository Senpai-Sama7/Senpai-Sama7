/**
 * Jest test setup and configuration
 * Global test utilities and mocks
 */

import { performance } from 'perf_hooks';

// Global test timeout
jest.setTimeout(30000);

// Mock console methods for cleaner test output
const originalConsole = { ...console };

beforeAll(() => {
  // Suppress console output during tests unless explicitly needed
  console.log = jest.fn();
  console.info = jest.fn();
  console.warn = jest.fn();
  console.error = jest.fn();
  console.debug = jest.fn();
});

afterAll(() => {
  // Restore console methods
  Object.assign(console, originalConsole);
});

// Global test utilities
declare global {
  namespace jest {
    interface Matchers<R> {
      toBeValidSVG(): R;
      toHavePerformanceUnder(milliseconds: number): R;
    }
  }
}

// Custom matchers
expect.extend({
  toBeValidSVG(received: string) {
    const pass = 
      typeof received === 'string' &&
      received.trim().startsWith('<svg') &&
      received.trim().endsWith('</svg>') &&
      received.includes('xmlns="http://www.w3.org/2000/svg"');

    if (pass) {
      return {
        message: () => `Expected ${received} not to be valid SVG`,
        pass: true,
      };
    } else {
      return {
        message: () => `Expected ${received} to be valid SVG`,
        pass: false,
      };
    }
  },

  toHavePerformanceUnder(received: () => void, milliseconds: number) {
    const startTime = performance.now();
    received();
    const endTime = performance.now();
    const duration = endTime - startTime;

    const pass = duration < milliseconds;

    if (pass) {
      return {
        message: () => `Expected function to take longer than ${milliseconds}ms, but it took ${duration.toFixed(2)}ms`,
        pass: true,
      };
    } else {
      return {
        message: () => `Expected function to complete under ${milliseconds}ms, but it took ${duration.toFixed(2)}ms`,
        pass: false,
      };
    }
  },
});

// Mock environment variables for tests
process.env.NODE_ENV = 'test';
process.env.LOG_LEVEL = 'ERROR'; // Suppress logs during tests

// Global error handler for unhandled promises
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
});

// Performance monitoring for tests
const performanceObserver = new PerformanceObserver((list) => {
  const entries = list.getEntries();
  entries.forEach((entry) => {
    if (entry.duration > 1000) { // Log slow operations
      console.warn(`Slow operation detected: ${entry.name} took ${entry.duration.toFixed(2)}ms`);
    }
  });
});

performanceObserver.observe({ entryTypes: ['measure'] });

// Test data factories
export const createTestSkill = (overrides: Partial<{ name: string; level: number; category: string }> = {}) => ({
  name: 'Test Skill',
  level: 50,
  category: 'general',
  ...overrides,
});

export const createTestSkills = (count: number = 5) => 
  Array.from({ length: count }, (_, i) => createTestSkill({
    name: `Skill ${i + 1}`,
    level: Math.floor(Math.random() * 100),
  }));

// Test utilities
export const measurePerformance = async (fn: () => Promise<void> | void): Promise<number> => {
  const startTime = performance.now();
  await fn();
  const endTime = performance.now();
  return endTime - startTime;
};

export const expectValidSVG = (svg: string) => {
  expect(svg).toBeValidSVG();
  expect(svg).toContain('xmlns="http://www.w3.org/2000/svg"');
};

export const expectAccessibleSVG = (svg: string) => {
  expect(svg).toContain('role="img"');
  expect(svg).toContain('aria-label');
  expect(svg).toContain('<title>');
  expect(svg).toContain('<desc>');
};

// Cleanup after each test
afterEach(() => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
});