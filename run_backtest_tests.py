#!/usr/bin/env python3
"""Script to run all backtest-related tests"""

import sys
import pytest
import argparse
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser(description='Run backtest test suite')
    parser.add_argument('--unit-only', action='store_true',
                       help='Run only unit tests')
    parser.add_argument('--integration-only', action='store_true',
                       help='Run only integration tests')
    parser.add_argument('--performance-only', action='store_true',
                       help='Run only performance tests')
    parser.add_argument('--helius-only', action='store_true',
                       help='Run only Helius integration tests')
    parser.add_argument('--coverage', action='store_true',
                       help='Generate coverage report')
    parser.add_argument('--html-report', action='store_true',
                       help='Generate HTML test report')
    parser.add_argument('--fail-fast', action='store_true',
                       help='Stop on first failure')
    
    args = parser.parse_args()
    
    # Base pytest arguments
    pytest_args = [
        '-c', 'env/tests/pytest_backtest.ini',
        '--verbose'
    ]
    
    # Add test selection based on arguments
    if args.unit_only:
        pytest_args.extend(['-m', 'unit'])
    elif args.integration_only:
        pytest_args.extend(['-m', 'integration'])
    elif args.performance_only:
        pytest_args.extend(['-m', 'performance'])
    elif args.helius_only:
        pytest_args.extend(['-m', 'helius'])
    
    # Add coverage if requested
    if args.coverage:
        pytest_args.extend([
            '--cov=env',
            '--cov-report=term-missing',
            '--cov-report=html:reports/coverage',
            '--cov-config=env/tests/pytest_backtest.ini'
        ])
    
    # Add HTML report if requested
    if args.html_report:
        report_dir = Path('reports') / 'test_results' / datetime.now().strftime('%Y%m%d_%H%M%S')
        report_dir.mkdir(parents=True, exist_ok=True)
        pytest_args.extend([
            f'--html={report_dir}/report.html',
            '--self-contained-html'
        ])
    
    # Add fail fast if requested
    if args.fail_fast:
        pytest_args.append('-x')
    
    # Add test timing
    pytest_args.extend([
        '--durations=10',
        '--durations-min=1.0'
    ])
    
    print(f"Running tests with arguments: {' '.join(pytest_args)}")
    
    try:
        # Run pytest with collected arguments
        result = pytest.main(pytest_args)
        
        # Generate summary
        if args.html_report:
            print(f"\nTest report generated at: {report_dir}/report.html")
        if args.coverage:
            print("\nCoverage report generated at: reports/coverage/index.html")
        
        sys.exit(result)
        
    except KeyboardInterrupt:
        print("\nTest execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError running tests: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
