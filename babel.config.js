module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        node: 'current'
      }
    }],
    '@babel/preset-typescript'
  ],
  plugins: [
    ['@babel/plugin-proposal-decorators', { legacy: true }],
    ['@babel/plugin-proposal-class-properties', { loose: true }],
    '@babel/plugin-proposal-object-rest-spread',
    '@babel/plugin-transform-runtime'
  ],
  env: {
    test: {
      plugins: [
        'babel-plugin-transform-typescript-metadata',
        'jest-hoist'
      ]
    },
    development: {
      plugins: [
        'source-map-support'
      ]
    },
    production: {
      plugins: [
        ['transform-remove-console', {
          exclude: ['error', 'warn', 'info']
        }]
      ]
    }
  },
  ignore: [
    'node_modules',
    'dist',
    'coverage',
    '**/*.test.ts',
    '**/*.spec.ts',
    '**/*.test.js',
    '**/*.spec.js',
    '**/tests/**',
    '**/mocks/**'
  ],
  sourceMaps: true,
  comments: false,
  minified: true,
  overrides: [
    {
      test: ['./env/**/*.ts'],
      presets: [
        '@babel/preset-typescript'
      ]
    },
    {
      test: ['./env/tests/**/*.ts'],
      presets: [
        ['@babel/preset-env', {
          targets: {
            node: 'current'
          }
        }],
        '@babel/preset-typescript'
      ]
    }
  ],
  assumptions: {
    setPublicClassFields: true,
    privateFieldsAsProperties: true,
    constantSuper: true,
    noDocumentAll: true,
    noClassCalls: true,
    superIsCallableConstructor: true,
    objectRestNoSymbols: true
  }
};
