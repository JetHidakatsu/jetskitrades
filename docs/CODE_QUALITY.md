# Code Quality Guidelines and Git Hooks

## Overview
This document describes the code quality tools and Git hooks implemented in the project to maintain high code quality standards.

## Git Hooks Setup
1. **Enable Git Hooks**
   ```bash
   git config core.hooksPath .githooks
   chmod +x .githooks/pre-commit
   chmod +x .githooks/pre-push
   ```

2. **Pre-commit Hook**
   - Runs before each commit
   - Executes the following checks:
     * Black formatter for consistent code style
     * Flake8 for PEP 8 compliance
     * MyPy for type checking
     * Pylint for code quality analysis

3. **Pre-push Hook**
   - Runs before pushing to remote
   - Executes the full test suite
   - Ensures all tests pass before code is shared

## Code Quality Tools

### Black Formatter
- Line length: 88 characters
- Consistent code style
- Configuration in `pyproject.toml`
- Automatically formats code before commit

### Flake8
- PEP 8 style guide enforcement
- Customized rules in `setup.cfg`
- Checks for:
  * Code style
  * Complexity
  * Error detection

### MyPy
- Static type checking
- Strict type enforcement
- Configuration in `setup.cfg`
- Prevents type-related bugs

### Pylint
- In-depth code analysis
- Style checking
- Error detection
- Configuration in `setup.cfg`

## Configuration Files

### setup.cfg
```ini
[flake8]
max-line-length = 88
extend-ignore = E203
exclude = .git,__pycache__,build,dist

[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
check_untyped_defs = True

[pylint]
max-line-length = 88
disable = C0111,R0903,C0103
ignore = migrations
good-names = i,j,k,ex,Run,_,id
```

### pyproject.toml
```toml
[tool.black]
line-length = 88
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
line_length = 88

[tool.pytest.ini_options]
minversion = "6.0"
addopts = "-ra -q"
testpaths = [
    "env/tests",
]
python_files = ["test_*.py"]
```

## Best Practices

1. **Before Committing**
   - Run formatters manually if needed: `black .`
   - Fix any linting issues: `pylint env/`
   - Check types: `mypy .`

2. **Handling Hook Failures**
   - Review error messages
   - Fix identified issues
   - Re-run commit/push

3. **Maintaining Quality**
   - Regular code reviews
   - Consistent style
   - Type annotations
   - Comprehensive tests

## Troubleshooting

1. **Hook Permission Issues**
   ```bash
   chmod +x .githooks/pre-commit
   chmod +x .githooks/pre-push
   ```

2. **Tool Installation**
   ```bash
   pip install black flake8 mypy pylint pytest
   ```

3. **Common Issues**
   - Black formatting conflicts
   - Type annotation errors
   - Test failures
   - Linting warnings

## Continuous Integration

The same quality checks are run in CI/CD pipelines to ensure:
- Consistent code quality
- All tests pass
- Type safety
- Style compliance
