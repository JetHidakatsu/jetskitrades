/** @type {import('jest').Config} */
module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  roots: ['<rootDir>/env'],
  testMatch: [
    '**/__tests__/**/*.+(ts|tsx|js)',
    '**/?(*.)+(spec|test).+(ts|tsx|js)'
  ],
  transform: {
    '^.+\\.(ts|tsx)$': 'ts-jest',
    '^.+\\.js$': 'babel-jest'
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/env/$1',
    '^@solana/web3.js$': '<rootDir>/env/tests/__mocks__/@solana/web3.js',
    '^@solana/spl-token$': '<rootDir>/env/tests/__mocks__/@solana/spl-token/index.js',
    '^@raydium-io/raydium-sdk$': '<rootDir>/env/tests/__mocks__/@raydium-io/raydium-sdk/index.js',
    '^@project-serum/serum$': '<rootDir>/env/tests/__mocks__/@project-serum/serum/index.js',
    '^qiskit$': '<rootDir>/env/tests/__mocks__/qiskit/index.js'
  },
  setupFilesAfterEnv: ['<rootDir>/env/tests/jest.setup.js'],
  collectCoverageFrom: [
    'env/**/*.{js,ts}',
    '!**/node_modules/**',
    '!**/dist/**',
    '!**/coverage/**',
    '!**/__mocks__/**',
    '!**/tests/**',
    '!**/*.d.ts',
    '!**/types/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],
  globals: {
    'ts-jest': {
      tsconfig: 'tsconfig.json',
      diagnostics: {
        warnOnly: true
      }
    }
  },
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/__mocks__/'
  ],
  clearMocks: true,
  resetMocks: true,
  restoreMocks: true,
  verbose: true,
  testTimeout: 30000,
  maxWorkers: '50%',
  errorOnDeprecated: true,
  testEnvironmentOptions: {
    url: 'http://localhost'
  },
  reporters: [
    'default',
    [
      'jest-junit',
      {
        outputDirectory: 'coverage',
        outputName: 'junit.xml',
        classNameTemplate: '{classname}',
        titleTemplate: '{title}',
        ancestorSeparator: ' › ',
        usePathForSuiteName: true
      }
    ]
  ],
  watchPlugins: [
    'jest-watch-typeahead/filename',
    'jest-watch-typeahead/testname'
  ],
  snapshotSerializers: [
    'jest-serializer-path',
    'jest-snapshot-serializer-raw'
  ],
  moduleDirectories: ['node_modules', 'env'],
  transformIgnorePatterns: [
    '/node_modules/(?!(@solana|@project-serum|@raydium-io)/)'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'clover', 'html'],
  automock: false
};
