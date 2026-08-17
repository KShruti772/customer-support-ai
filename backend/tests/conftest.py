"""
Pytest configuration and fixtures for tests.

Disables rate limiting during tests to avoid false positives.
"""

import os

# Disable rate limiting for all tests
os.environ["DISABLE_RATE_LIMIT"] = "true"
