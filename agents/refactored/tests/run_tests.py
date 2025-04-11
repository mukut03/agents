"""
Test runner for the refactored agent framework.
"""
import unittest
import sys
import os

# Add the parent directory to the path so that imports work correctly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

# Import the test modules
from agents.refactored.tests.test_tool_executor import TestToolExecutor
from agents.refactored.tests.test_agent_action_extraction import TestAgentActionExtraction
from agents.refactored.tests.test_routes_tools import TestRoutesTools


def run_tests():
    """Run all tests."""
    # Create a test suite
    test_suite = unittest.TestSuite()
    
    # Add the test cases
    test_suite.addTest(unittest.makeSuite(TestToolExecutor))
    test_suite.addTest(unittest.makeSuite(TestAgentActionExtraction))
    test_suite.addTest(unittest.makeSuite(TestRoutesTools))
    
    # Run the tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return the result
    return result


if __name__ == "__main__":
    # Run the tests
    result = run_tests()
    
    # Exit with a non-zero code if there were failures
    sys.exit(len(result.failures) + len(result.errors))
