# Git Setup and Code Quality Guidelines

This document explains how to set up your development environment for proper Git integration and code quality checks.

## Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/my-solana-bot.git
cd my-solana-bot
```

2. Run the setup script:
```bash
python setup_git_hooks.py
```

This script will:
- Install pre-commit and other dependencies
- Set up Git hooks
- Configure proper line endings
- Run initial code formatting

## Code Quality Tools

The project uses several tools to maintain code quality:

- **black**: Code formatter that enforces consistent style
- **isort**: Import statement organizer
- **flake8**: Code linter that checks for style and potential errors
- **mypy**: Static type checker

These tools run automatically on commit, but you can also run them manually:

```bash
# Format code
black .

# Sort imports
isort .

# Run linter
flake8

# Run type checker
mypy .
```

## Git Workflow

1. Before committing changes:
   - Your code will be automatically formatted
   - Imports will be sorted
   - Type hints will be checked
   - Line endings will be normalized

2. If the pre-commit hook fails:
   - Review the error messages
   - Fix any issues
   - Stage the changes
   - Try committing again

3. To temporarily bypass hooks (not recommended):
```bash
git commit --no-verify
```

## Line Length and Formatting

- Maximum line length is 88 characters
- Use spaces for indentation (4 spaces)
- Follow PEP 8 style guidelines
- Use type hints for all function definitions

## Common Issues

1. **Line too long errors (E501)**:
   - Break long lines into multiple lines
   - Use parentheses for line continuation
   - Consider using variables for long strings

2. **Import sorting issues (F401, F403)**:
   - Use explicit imports instead of *
   - Remove unused imports
   - Group imports properly (standard library, third-party, local)

3. **Line ending issues**:
   - Don't manually change line endings
   - Let Git handle it through .gitattributes

## IDE Integration

### VS Code
The project includes VS Code settings that configure:
- Format on save
- Python linting
- Type checking
- Line ending handling

Install recommended extensions:
- Python
- Pylance
- GitLens
- Git Graph

### PyCharm
Configure PyCharm to:
- Use black as formatter
- Enable type checking
- Use project's pylint settings

## Troubleshooting

If you encounter issues:

1. **Hook installation fails**:
```bash
pre-commit uninstall
pre-commit clean
python setup_git_hooks.py
```

2. **Line ending issues**:
```bash
# Reset Git's line ending handling
git rm --cached -r .
git reset --hard
python setup_git_hooks.py
```

3. **Formatting conflicts**:
```bash
# Reset formatting
black .
isort .
git add .
git commit
```

## Additional Tips

1. **Working with Long Lines**:
```python
# Break function arguments
def long_function_name(
    arg1: str,
    arg2: int,
    arg3: List[str],
) -> None:
    pass

# Break long strings
long_string = (
    "This is a very long string that needs "
    "to be broken into multiple lines"
)

# Break long lists/dicts
my_list = [
    item1,
    item2,
    item3,
]
```

2. **Import Organization**:
```python
# Standard library imports
import os
import sys
from typing import List, Optional

# Third-party imports
import pytest
from solana.rpc.async_api import AsyncClient

# Local imports
from .config import CONFIG
from .utils import helper_function
```

3. **Type Hints**:
```python
from typing import Dict, List, Optional, Union

def process_data(
    data: List[Dict[str, Any]],
    filter_key: Optional[str] = None,
) -> Union[List[str], None]:
    pass
```

Remember to run the setup script whenever you clone the repository to a new machine or if you encounter any Git-related issues.
