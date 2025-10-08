/** @type {import('jest').Config} */
module.exports = {
  // Test environment
  preset: 'ts-jest',
  testEnvironment: 'node',
  
  // Test discovery
  roots: ['<rootDir>/tests'],
  testMatch: [
    '**/__tests__/**/*.ts',
    '**/?(*.)+(spec|test).ts'
  ],
  
  // TypeScript configuration
  transform: {
    '^.+\\.ts$': 'ts-jest',
  },
  
  // Module resolution
  moduleFileExtensions: ['ts', 'js', 'json'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/scripts/$1',
  },
  
  // Coverage configuration
  collectCoverage: true,
  collectCoverageFrom: [
    'scripts/**/*.ts',
    '!scripts/**/*.d.ts',
    '!scripts/**/*.test.ts',
    '!scripts/**/*.spec.ts',
    '!**/node_modules/**',
    '!**/dist/**',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',
    'text-summary',
    'lcov',
    'html',
    'json',
    'clover'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
  },
  
  // Test setup and teardown
  setupFilesAfterEnv: ['<rootDir>/tests/setup.ts'],
  
  // Test timeout
  testTimeout: 30000,
  
  // Verbose output
  verbose: true,
  
  // Error handling
  errorOnDeprecated: true,
  
  // Performance
  maxWorkers: '50%',
  
  // Reporting
  reporters: [
    'default',
    ['jest-junit', {
      outputDirectory: 'coverage',
      outputName: 'junit.xml',
    }],
    ['jest-html-reporters', {
      publicPath: 'coverage/html',
      filename: 'jest-report.html',
    }],
  ],
  
  // Watch mode
  watchPathIgnorePatterns: [
    '<rootDir>/node_modules/',
    '<rootDir>/dist/',
    '<rootDir>/coverage/',
  ],
  
  // Global configuration
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json',
      isolatedModules: true,
    },
  },
  
  // Clear mocks between tests
  clearMocks: true,
  restoreMocks: true,
  
  // Fail fast
  bail: false,
  
  // Test result processor
  testResultsProcessor: 'jest-sonar-reporter',
};