import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock

# Add current dir to path
sys.path.append(os.getcwd())

from backend import models, agents

class TestAgentTools(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.query_mock = MagicMock()
        self.mock_db.query.return_value = self.query_mock
        # Chaining implementation for filter
        self.query_mock.filter.return_value = self.query_mock
        
    def test_get_expenses_tool_date_range(self):
        # We can't easily test the actual SQLAlchemy filter logic with mocks without complex setup.
        # But we can test that filter() is called with correct arguments or at least called twice for date range.
        
        # ACT
        agents.get_expenses_tool(self.mock_db, category="Food", date="2025-11-01", end_date="2025-11-30")
        
        # ASSERT
        # Verify query was created for Expense model
        self.mock_db.query.assert_called_with(models.Expense)
        
        # Verify filter was called (for category, date, end_date)
        # We expect at least 3 filter calls
        self.assertTrue(self.query_mock.filter.call_count >= 3)
        
        print("Test passed: query construction appears correct with end_date.")

if __name__ == '__main__':
    unittest.main()
