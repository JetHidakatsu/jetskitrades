module.exports = {
  semi: true,
  trailingComma: 'es5',
  singleQuote: true,
  printWidth: 100,
  tabWidth: 2,
  useTabs: false,
  bracketSpacing: true,
  arrowParens: 'avoid',
  endOfLine: 'lf',
  overrides: [
    {
      files: '*.{ts,tsx}',
      options: {
        parser: 'typescript',
      },
    },
    {
      files: '*.{js,jsx}',
      options: {
        parser: 'babel',
      },
    },
    {
      files: '*.json',
      options: {
        parser: 'json',
      },
    },
    {
      files: '*.md',
      options: {
        parser: 'markdown',
      },
    },
    {
      files: '*.yml',
      options: {
        parser: 'yaml',
      },
    },
  ],
  importOrder: [
    '^@solana/(.*)$',
    '^@raydium-io/(.*)$',
    '^@project-serum/(.*)$',
    '^@/(.*)$',
    '^[./]',
  ],
  importOrderSeparation: true,
  importOrderSortSpecifiers: true,
};
