module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  plugins: [
    '@typescript-eslint',
    'jest'
  ],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:jest/recommended',
    'prettier'
  ],
  env: {
    node: true,
    jest: true,
    es2020: true
  },
  rules: {
    '@typescript-eslint/explicit-module-boundary-types': 'off',
    '@typescript-eslint/no-explicit-any': 'off',
    '@typescript-eslint/no-unused-vars': ['error', { 
      'argsIgnorePattern': '^_',
      'varsIgnorePattern': '^_'
    }],
    'no-console': ['warn', { 
      allow: ['warn', 'error', 'info', 'debug'] 
    }],
    'jest/no-disabled-tests': 'warn',
    'jest/no-focused-tests': 'error',
    'jest/no-identical-title': 'error',
    'jest/prefer-to-have-length': 'warn',
    'jest/valid-expect': 'error'
  },
  settings: {
    'import/resolver': {
      typescript: {}
    }
  },
  overrides: [
    {
      files: ['*.js'],
      rules: {
        '@typescript-eslint/no-var-requires': 'off'
      }
    },
    {
      files: ['*.test.ts', '*.test.js', '*.spec.ts', '*.spec.js'],
      rules: {
        '@typescript-eslint/no-explicit-any': 'off',
        'jest/expect-expect': 'off'
      }
    }
  ]
};
