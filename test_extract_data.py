import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from extract_data import get_google_sheet_data

class TestGoogleSheetExtraction(unittest.TestCase):
    """Test cases for Google Sheet data extraction functionality"""

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_successful_data_extraction(self, mock_build, mock_credentials):
        # Mock data
        mock_values = [
            ['Email Address', 'Tool Used', 'Feature', 'Context Awareness Rating'],
            ['test@email.com', 'Tool1', 'Feature1', '4'],
        ]
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': mock_values
        }

        # Execute function
        result = get_google_sheet_data()

        # Assertions
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(len(result) > 0)

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_empty_sheet(self, mock_build, mock_credentials):
        # Mock empty response
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {
            'values': []
        }

        # Execute function
        result = get_google_sheet_data()

        # Assertions
        self.assertIsNone(result)

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_api_error(self, mock_build, mock_credentials):
        # Mock API error
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.side_effect = Exception("API Error")

        # Execute function
        result = get_google_sheet_data()

        # Assertions
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()