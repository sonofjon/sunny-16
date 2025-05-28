"""Test runner script to execute all unit tests.

This script runs all test modules and provides a summary of results.
"""

import sys
import unittest


def run_all_tests():
    """Run all test modules and return results."""
    # Discover and run all tests
    loader = unittest.TestLoader()
    start_dir = "."
    suite = loader.discover(start_dir, pattern="test_*.py")

    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result


if __name__ == "__main__":
    print("Running all tests for Sunny 16 Calculator...")
    print("=" * 50)

    result = run_all_tests()

    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.failures:
        print("\nFailures:")
        for test, _ in result.failures:
            print(f"- {test}")

    if result.errors:
        print("\nErrors:")
        for test, _ in result.errors:
            print(f"- {test}")

    # Exit with appropriate code
    if result.failures or result.errors:
        sys.exit(1)
    else:
        print("\nAll tests passed! ✅")
        sys.exit(0)
