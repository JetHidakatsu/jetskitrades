# Debugging Guide

This guide explains how to use the debugging setup for the Solana bot project.

## Setup

The project includes a comprehensive debugging setup with:

1. Debug test runner (`run_tests_debug.py`)
2. VSCode launch configurations
3. Environment variable management
4. Logging configuration

## Using VSCode Debug Configurations

The following debug configurations are available:

### 1. Debug Current Test File
- Name: `Python: Debug Tests`
- Use when: You want to debug the currently open test file
- How to use:
  1. Open the test file you want to debug
  2. Set breakpoints in the code
  3. Press F5 or select "Python: Debug Tests" from the debug menu

### 2. Debug All Tests
- Name: `Python: Debug All Tests`
- Use when: You want to debug all tests in the project
- How to use:
  1. Set breakpoints in any test files
  2. Select "Python: Debug All Tests" from the debug menu
  3. Press F5

### 3. Debug Current File
- Name: `Python: Debug Current File`
- Use when: You want to debug any Python file (not just tests)
- How to use:
  1. Open the file you want to debug
  2. Set breakpoints
  3. Select "Python: Debug Current File" from the debug menu

### 4. Debug Specific Test Categories
- Available configurations:
  - `Python: Debug Backtest Tests`
  - `Python: Debug Integration Tests`
  - `Python: Debug Trading Tests`
- Use when: You want to focus on a specific category of tests
- How to use:
  1. Set breakpoints in relevant test files
  2. Select the appropriate configuration from the debug menu
  3. Press F5

## Setting Breakpoints

1. Click in the left margin of the code editor to set a breakpoint
2. When execution reaches the breakpoint:
   - Examine variable values in the Variables panel
   - Use the Debug Console to evaluate expressions
   - Step through code using the debug toolbar

## Environment Variables

The debug setup automatically configures:
- `PYTHONPATH`: Set to the project root
- `TESTING`: Set to "true"
- Additional environment variables can be added in `launch.json`

## Logging

The debug setup includes comprehensive logging:
- Log level: DEBUG
- Format: Timestamp - Level - Message
- Output: Visible in the Debug Console

## Common Debugging Tasks

### Debugging Test Failures
1. Open the failing test file
2. Set breakpoints around the failing assertion
3. Use "Python: Debug Tests" configuration
4. Examine variables at the breakpoint

### Debugging Integration Issues
1. Use "Python: Debug Integration Tests" configuration
2. Set breakpoints in both the test and the code being tested
3. Step through to see the interaction between components

### Debugging Performance Issues
1. Set breakpoints at the start and end of the suspected slow operation
2. Use the Debug Console to time operations
3. Examine variables for unexpected data sizes or operations

## Tips

1. Use conditional breakpoints for complex debugging:
   - Right-click on a breakpoint
   - Select "Edit Breakpoint"
   - Add a condition

2. Use logpoints for non-breaking debugging:
   - Right-click the left margin
   - Select "Add Logpoint"
   - Enter a message with {expressions}

3. Use the Watch panel to monitor specific variables:
   - Click the + in the Watch panel
   - Enter the variable name or expression

4. Debug with pytest features:
   - Use `pytest.set_trace()` in code
   - Use the `--pdb` option for automatic breaks on failures

## Troubleshooting

### Common Issues

1. Breakpoints not hitting:
   - Verify PYTHONPATH is set correctly
   - Check if the code is actually being executed
   - Try clearing the pytest cache

2. Environment variables not set:
   - Check launch.json configuration
   - Verify run_tests_debug.py is being used
   - Try restarting VSCode

3. Test discovery issues:
   - Verify test file names match pattern test_*.py
   - Check pytest.ini configuration
   - Try clearing pytest cache

### Getting Help

If you encounter issues:
1. Check the Debug Console for error messages
2. Review the test output for any pytest errors
3. Verify your VSCode Python extension is up to date
4. Ensure all project dependencies are installed

## Additional Resources

- [VSCode Python Debugging Documentation](https://code.visualstudio.com/docs/python/debugging)
- [pytest Documentation](https://docs.pytest.org/)
- [Python Debugging Tips](https://docs.python.org/3/library/pdb.html)
