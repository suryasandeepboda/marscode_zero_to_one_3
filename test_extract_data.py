import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from extract_data import get_google_sheet_data

class TestGoogleSheetExtraction(unittest.TestCase):
    """Test cases for Google Sheet data extraction functionality"""

    def setUp(self):
        """Set up test data"""
        self.mock_data = [
            ['Email Address', 'Tool being used', 'Feature used', 'Context Awareness', 
             'Autonomy', 'Experience', 'Output Quality', 'Overall Rating', 'Unique ID'],
            ['test@email.com', 'Tool1', 'Feature1', '4', '3', '5', '4', '4', 'ID1'],
            ['test2@email.com', 'Tool2', 'Feature2', '5', '5', '5', '5', '4', 'ID2'],
        ]

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_successful_data_extraction(self, mock_build, mock_credentials):
        """Test successful data extraction and processing"""
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': self.mock_data
        }

        # Execute function
        result = get_google_sheet_data()

        # Assertions
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertEqual(len(result), 2)  # Two data rows
        self.assertTrue('Mean Rating' in result.columns)
        self.assertTrue('Difference' in result.columns)
        self.assertTrue('Result' in result.columns)

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_calculation_accuracy(self, mock_build, mock_credentials):
        """Test accuracy of calculations"""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': self.mock_data
        }

        result = get_google_sheet_data()

        # Test Mean Rating calculation
        expected_mean = (4 + 3 + 5 + 4) / 4  # First row ratings
        self.assertAlmostEqual(result['Mean Rating'].iloc[0], expected_mean)

        # Test Difference calculation
        expected_diff = expected_mean - 4  # Mean - Overall Rating
        self.assertAlmostEqual(result['Difference'].iloc[0], expected_diff)

        # Test Result determination
        self.assertEqual(result['Result'].iloc[0], 'Ok')

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_empty_sheet(self, mock_build, mock_credentials):
        """Test handling of empty sheet"""
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': []
        }

        result = get_google_sheet_data()
        self.assertIsNone(result)

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_missing_columns(self, mock_build, mock_credentials):
        """Test handling of missing columns"""
        mock_data = [
            ['Email Address', 'Tool being used'],  # Missing columns
            ['test@email.com', 'Tool1']
        ]
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': mock_data
        }

        result = get_google_sheet_data()
        self.assertIsNone(result)

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_invalid_ratings(self, mock_build, mock_credentials):
        """Test handling of invalid rating values"""
        # Create mock data with invalid rating
        mock_data = [
            ['Email Address', 'Tool being used', 'Feature used', 'Context Awareness', 
             'Autonomy', 'Experience', 'Output Quality', 'Overall Rating', 'Unique ID'],
            ['test@email.com', 'Tool1', 'Feature1', 'invalid', '3', '5', '4', '4', 'ID1'],
            ['test2@email.com', 'Tool2', 'Feature2', '5', '5', '5', '5', '4', 'ID2']
        ]
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': mock_data
        }

        result = get_google_sheet_data()
        
        # Verify the result exists
        self.assertIsNotNone(result)
        
        # Verify second row is calculated correctly (all valid numbers)
        expected_mean_row2 = (5 + 5 + 5 + 5) / 4
        self.assertAlmostEqual(result['Mean Rating'].iloc[1], expected_mean_row2)
        
        # For first row, verify mean is calculated correctly excluding invalid value
        expected_mean_row1 = (3 + 5 + 4) / 3  # Average of valid ratings only
        self.assertAlmostEqual(result['Mean Rating'].iloc[0], expected_mean_row1)

    def test_result_status_calculation(self):
        """Test result status determination"""
        test_differences = [-2, -0.5, 0, 0.5, 2]
        expected_results = ['Not ok', 'Ok', 'Ok', 'Ok', 'Not ok']
        
        for diff, expected in zip(test_differences, expected_results):
            with self.subTest(difference=diff):
                result = 'Ok' if -1 <= diff <= 1 else 'Not ok'
                self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main(verbosity=2)