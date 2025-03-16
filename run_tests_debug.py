"""
Script to run all tests with debugging configuration
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for debugging"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.environ['PYTHONPATH'] = project_root
    os.environ['TESTING'] = 'true'
    os.environ['PYTEST_ADDOPTS'] = '--no-cov'
    logger.info(f"Set PYTHONPATH to {project_root}")
    logger.info("Environment variables configured for debugging")

def run_tests(test_path=None):
    """Run tests with debugging configuration"""
    cmd = [
        sys.executable,
        '-m',
        'pytest',
        '-v',
        '--tb=short',
        '-s'
    ]

    if test_path:
        cmd.append(test_path)
    else:
        cmd.append('env/tests/')

    logger.info(f"Running tests with command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        logger.info("Tests completed successfully")
    except subprocess.CalledProcessError as e:
        logger.error(f"Tests failed with exit code {e.returncode}")
        sys.exit(1)

if __name__ == '__main__':
    setup_environment()
    
    if len(sys.argv) > 1:
        # Run specific test file or directory
        test_path = sys.argv[1]
        logger.info(f"Running tests from: {test_path}")
        run_tests(test_path)
    else:
        # Run all tests
        logger.info("Running all tests")
        run_tests()
