#!/usr/bin/env python3
"""Setup script for documentation tools and Git hooks."""

import subprocess
import sys
from pathlib import Path


def setup_docs():
    """Set up documentation tools and Git hooks."""
    project_root = Path(__file__).parent.parent

    print("Setting up documentation tools...")

    # Install documentation dependencies
    requirements_file = project_root / "tools" / "requirements-docs.txt"
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(requirements_file)],
            check=True,
        )
        print("✓ Installed documentation dependencies")
    except subprocess.CalledProcessError:
        print("✗ Failed to install documentation dependencies")
        return False

    # Create docs/api directory
    api_docs_dir = project_root / "docs" / "api"
    api_docs_dir.mkdir(parents=True, exist_ok=True)
    print("✓ Created docs/api directory")

    # Configure Git hooks
    hooks_dir = project_root / ".githooks"

    # Update pre-commit hook
    pre_commit = hooks_dir / "pre-commit"
    pre_commit_content = """#!/bin/bash

echo "Running pre-commit checks..."

# Run black formatter
echo "Running black formatter..."
python -m black . || exit 1

# Run flake8
echo "Running flake8..."
python -m flake8 . || exit 1

# Run mypy type checking
echo "Running type checker..."
python -m mypy . || exit 1

# Run pylint
echo "Running pylint..."
python -m pylint env/ || exit 1

# Generate documentation
echo "Generating documentation..."
python tools/generate_docs.py || exit 1

# Add generated documentation to the commit
git add docs/api/

echo "All pre-commit checks passed!"
"""
    pre_commit.write_text(pre_commit_content)
    pre_commit.chmod(0o755)
    print("✓ Updated pre-commit hook")

    # Configure Git to use the hooks
    try:
        subprocess.run(
            ["git", "config", "core.hooksPath", ".githooks"],
            cwd=project_root,
            check=True,
        )
        print("✓ Configured Git hooks")
    except subprocess.CalledProcessError:
        print("✗ Failed to configure Git hooks")
        return False

    print("\nDocumentation setup complete! The system will now:")
    print("1. Generate API documentation from docstrings")
    print("2. Update documentation on each commit")
    print("3. Keep documentation in sync with code changes")

    return True


if __name__ == "__main__":
    if setup_docs():
        sys.exit(0)
    else:
        sys.exit(1)
