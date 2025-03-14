#!/usr/bin/env python3
"""Development environment setup and testing utility"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path


def check_python_version():
    """Check if Python version meets requirements"""
    required_version = (3, 8)
    current_version = sys.version_info[:2]

    if current_version < required_version:
        print(
            f"Error: Python {required_version[0]}.{required_version[1]} or higher is required"
        )
        sys.exit(1)


def setup_virtual_environment():
    """Create and activate virtual environment"""
    if not os.path.exists("venv"):
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)

    # Determine the correct activate script based on OS
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
    else:
        activate_script = "venv/bin/activate"

    print(f"To activate the virtual environment, run: source {activate_script}")


def install_dependencies(dev=False):
    """Install project dependencies"""
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]

    if dev:
        pip_cmd = [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            "requirements.txt",
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-timeout",
            "pytest-xdist",
            "pytest-mock",
            "pytest-randomly",
            "pytest-sugar",
            "coverage",
            "asynctest",
            "freezegun",
            "responses",
        ]

    print("Installing dependencies...")
    subprocess.run(pip_cmd, check=True)


def setup_env_file():
    """Setup environment configuration file"""
    if not os.path.exists(".env"):
        print("Creating .env file from template...")
        shutil.copy(".env.example", ".env")
        print("Please edit .env with your configuration settings")


def run_tests(coverage=False):
    """Run test suite"""
    test_cmd = ["pytest", "-v"]

    if coverage:
        test_cmd.extend(["--cov=env", "--cov-report=html"])

    print("Running tests...")
    subprocess.run(test_cmd, check=True)


def setup_git_hooks():
    """Setup Git hooks for development"""
    hooks_dir = Path(".git/hooks")

    if not hooks_dir.exists():
        print("Git hooks directory not found. Initializing Git repository...")
        subprocess.run(["git", "init"], check=True)
        hooks_dir.mkdir(parents=True, exist_ok=True)

    # Create pre-commit hook
    pre_commit = hooks_dir / "pre-commit"
    with open(pre_commit, "w") as f:
        f.write(
            """#!/bin/sh
# Run tests before commit
python -m pytest || exit 1
"""
        )

    # Make hook executable
    pre_commit.chmod(0o755)
    print("Git hooks installed")


def check_system_dependencies():
    """Check system dependencies"""
    dependencies = {
        "git": "Git is required for version control",
        "python3": "Python 3.8 or higher is required",
    }

    missing = []
    for cmd, message in dependencies.items():
        try:
            subprocess.run(
                [cmd, "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        except FileNotFoundError:
            missing.append(f"{cmd}: {message}")

    if missing:
        print("Missing system dependencies:")
        for msg in missing:
            print(f"- {msg}")
        sys.exit(1)


def setup_metrics_directory():
    """Setup directory for metrics and logs"""
    metrics_dir = Path("metrics")
    metrics_dir.mkdir(exist_ok=True)

    # Create directories for different metric types
    (metrics_dir / "performance").mkdir(exist_ok=True)
    (metrics_dir / "latency").mkdir(exist_ok=True)
    (metrics_dir / "logs").mkdir(exist_ok=True)


def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(
        description="Development environment setup utility"
    )

    parser.add_argument(
        "--dev", action="store_true", help="Install development dependencies"
    )
    parser.add_argument("--test", action="store_true", help="Run test suite")
    parser.add_argument(
        "--coverage", action="store_true", help="Run tests with coverage report"
    )
    parser.add_argument("--hooks", action="store_true", help="Setup Git hooks")

    args = parser.parse_args()

    try:
        # System checks
        check_python_version()
        check_system_dependencies()

        # Basic setup
        setup_virtual_environment()
        install_dependencies(dev=args.dev)
        setup_env_file()
        setup_metrics_directory()

        # Optional setup
        if args.hooks:
            setup_git_hooks()

        # Run tests if requested
        if args.test or args.coverage:
            run_tests(coverage=args.coverage)

        print("\nSetup completed successfully!")
        print("\nNext steps:")
        print("1. Activate your virtual environment")
        print("2. Edit the .env file with your settings")
        print("3. Run 'python main.py --mode simulate' to test the bot")

    except subprocess.CalledProcessError as e:
        print(f"Error during setup: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
