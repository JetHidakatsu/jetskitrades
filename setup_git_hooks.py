#!/usr/bin/env python3
"""Set up Git hooks and install required dependencies."""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command):
    """Run a shell command and print output."""
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """Main setup function."""
    # Get project root directory
    project_root = Path(__file__).parent.absolute()
    
    print("Setting up Git hooks and development environment...")
    
    # Install pre-commit if not already installed
    print("\nInstalling pre-commit...")
    run_command("pip install pre-commit")
    
    # Install project dependencies
    print("\nInstalling project dependencies...")
    run_command("pip install -r requirements.txt")
    
    # Install pre-commit hooks
    print("\nInstalling pre-commit hooks...")
    run_command("pre-commit install")
    
    # Initialize Git hooks directory if it doesn't exist
    hooks_dir = project_root / ".git" / "hooks"
    if not hooks_dir.exists():
        print("\nCreating Git hooks directory...")
        hooks_dir.mkdir(parents=True, exist_ok=True)
    
    # Make pre-commit hook executable
    pre_commit_hook = project_root / ".githooks" / "pre-commit"
    if pre_commit_hook.exists():
        print("\nMaking pre-commit hook executable...")
        pre_commit_hook.chmod(0o755)
    
    # Configure Git to use LF line endings
    print("\nConfiguring Git line endings...")
    run_command('git config core.autocrlf false')
    run_command('git config core.eol lf')
    
    # Run pre-commit on all files
    print("\nRunning pre-commit on all files...")
    run_command("pre-commit run --all-files")
    
    print("\nSetup complete! Your development environment is now configured.")
    print("\nNotes:")
    print("1. The pre-commit hook will now run automatically on git commit")
    print("2. Line endings will be automatically normalized")
    print("3. Code formatting will be enforced using black, isort, and flake8")
    print("\nIf you need to bypass hooks temporarily, use: git commit --no-verify")

if __name__ == "__main__":
    main()
