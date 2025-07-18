"""
Script to run tests
"""
import pytest
import sys

if __name__ == "__main__":
    # Run tests with verbose output
    sys.exit(pytest.main(["-v", "--asyncio-mode=auto"]))