import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
from extract_data import clear_target_sheet, write_to_target_sheet, get_google_sheet_data

class TestGoogleSheetExtraction(unittest.TestCase):
    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_clear_target_sheet_success(self, mock_build, mock_credentials):
        # Setup mock
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().clear().execute.return_value = {}
        
        # Execute
        result = clear_target_sheet()
        
        # Assert
        self.assertIsNotNone(result)
        mock_service.spreadsheets().values().clear.assert_called_once()

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_clear_target_sheet_failure(self, mock_build, mock_credentials):
        # Setup mock
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().clear().execute.side_effect = Exception("API Error")
        
        # Execute
        result = clear_target_sheet()
        
        # Assert
        self.assertIsNone(result)

    def test_write_to_target_sheet_success(self):
        # Setup test data
        df = pd.DataFrame({
            'Email Address': ['test@example.com'],
            'Tool being used': ['Tool1'],
            'Feature used': ['Feature1'],
            'Context Awareness': [4.0],
            'Autonomy': [4.0],
            'Experience': [4.0],
            'Output Quality': [4.0],
            'Overall Rating': [4.0],
            'Mean Rating': [4.0],
            'Difference': [0.0],
            'Result': ['Ok'],
            'Unique ID': ['ID1']
        })
        
        mock_service = MagicMock()
        mock_service.spreadsheets().values().update().execute.return_value = {}
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        # Execute
        result = write_to_target_sheet(df, mock_service)
        
        # Assert
        self.assertTrue(result)
        mock_service.spreadsheets().values().update.assert_called_once()
        mock_service.spreadsheets().batchUpdate.assert_called()

    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_success(self, mock_credentials, mock_build):
        # Setup mock data
        mock_values = [
            ['Email Address', 'Tool being used', 'Feature used', 'Context Awareness', 
             'Autonomy', 'Experience', 'Output Quality', 'Overall Rating', 'Unique ID'],
            ['test@example.com', 'Tool1', 'Feature1', '4', '4', '4', '4', '4', 'ID1']
        ]
        
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {'values': mock_values}
        mock_service.spreadsheets().values().clear().execute.return_value = {}
        mock_service.spreadsheets().values().update().execute.return_value = {}
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        # Execute
        result = get_google_sheet_data()
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 1)
        self.assertEqual(result['Result'].iloc[0], 'Ok')

    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_no_data(self, mock_credentials, mock_build):
        # Setup mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {'values': []}
        
        # Execute
        result = get_google_sheet_data()
        
        # Assert
        self.assertIsNone(result)

    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_api_error(self, mock_credentials, mock_build):
        # Setup mock service to raise exception
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.side_effect = Exception("API Error")
        
        # Execute
        result = get_google_sheet_data()
        
        # Assert
        self.assertIsNone(result)

    def test_write_to_target_sheet_failure(self):
        # Setup test data
        df = pd.DataFrame({
            'Email Address': ['test@example.com'],
            'Result': ['Ok']
        })
        
        mock_service = MagicMock()
        mock_service.spreadsheets().values().update().execute.side_effect = Exception("API Error")
        
        # Execute
        result = write_to_target_sheet(df, mock_service)
        
        # Assert
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()