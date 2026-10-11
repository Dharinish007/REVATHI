"""Run this project's checks: python run_checks.py"""
import sys
import unittest

suite = unittest.defaultTestLoader.discover("checks", pattern="*_check.py")
result = unittest.TextTestRunner(verbosity=1).run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
