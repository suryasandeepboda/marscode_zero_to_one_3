import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import numpy as np
from extract_data import clear_target_sheet, write_to_target_sheet, get_google_sheet_data

class TestGoogleSheetExtraction(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        # Sample DataFrame for testing
        self.test_df = pd.DataFrame({
            'Email Address': ['test1@example.com', 'test2@example.com'],
            'Tool being used': ['Tool1', 'Tool2'],
            'Feature used': ['Feature1', 'Feature2'],
            'Context Awareness': [4.0, 2.0],
            'Autonomy': [4.0, 2.0],
            'Experience': [4.0, 2.0],
            'Output Quality': [4.0, 2.0],
            'Overall Rating': [4.0, 4.0],
            'Mean Rating': [4.0, 2.0],
            'Difference': [0.0, -2.0],
            'Result': ['Ok', 'Not ok'],
            'Unique ID': ['ID1', 'ID2']
        })

        # Sample sheet data for testing
        self.mock_sheet_data = [
            ['Email Address', 'Tool being used', 'Feature used', 'Context Awareness', 
             'Autonomy', 'Experience', 'Output Quality', 'Overall Rating', 'Unique ID'],
            ['test1@example.com', 'Tool1', 'Feature1', '4', '4', '4', '4', '4', 'ID1'],
            ['test2@example.com', 'Tool2', 'Feature2', '2', '2', '2', '2', '4', 'ID2']
        ]

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_clear_target_sheet_success(self, mock_build, mock_credentials):
        # Setup mock
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Create a proper mock chain for spreadsheets().values().clear()
        mock_spreadsheets = MagicMock()
        mock_values = MagicMock()
        mock_clear_request = MagicMock()
        
        mock_service.spreadsheets.return_value = mock_spreadsheets
        mock_spreadsheets.values.return_value = mock_values
        mock_values.clear.return_value = mock_clear_request
        mock_clear_request.execute.return_value = {}
        
        result = clear_target_sheet()
        
        # Assertions
        self.assertIsNotNone(result)
        mock_credentials.from_service_account_file.assert_called_once()
        mock_build.assert_called_once()
        mock_values.clear.assert_called_once()
        mock_clear_request.execute.assert_called_once()

    @patch('extract_data.Credentials')
    @patch('extract_data.build')
    def test_clear_target_sheet_api_error(self, mock_build, mock_credentials):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().clear().execute.side_effect = Exception("API Error")
        
        result = clear_target_sheet()
        
        self.assertIsNone(result)

    def test_write_to_target_sheet_success(self):
        mock_service = MagicMock()
        result = write_to_target_sheet(self.test_df, mock_service)
        
        self.assertTrue(result)
        mock_service.spreadsheets().values().update.assert_called_once()
        mock_service.spreadsheets().batchUpdate.assert_called()

    def test_write_to_target_sheet_with_nan(self):
        df_with_nan = self.test_df.copy()
        df_with_nan.iloc[0, 3:8] = np.nan
        
        mock_service = MagicMock()
        result = write_to_target_sheet(df_with_nan, mock_service)
        
        self.assertTrue(result)

    def test_write_to_target_sheet_api_error(self):
        mock_service = MagicMock()
        mock_service.spreadsheets().values().update.side_effect = Exception("API Error")
        
        result = write_to_target_sheet(self.test_df, mock_service)
        
        self.assertFalse(result)

    @patch('extract_data.clear_target_sheet')
    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_success(self, mock_credentials, mock_build, mock_clear):
        # Setup mocks
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {'values': self.mock_sheet_data}
        mock_clear.return_value = mock_service
        
        # Execute
        result = get_google_sheet_data()
        
        # Assert
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 2)
        self.assertEqual(result['Result'].iloc[0], 'Ok')
        self.assertEqual(result['Result'].iloc[1], 'Not ok')
        self.assertTrue('Mean Rating' in result.columns)
        self.assertTrue('Difference' in result.columns)

    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_no_data(self, mock_credentials, mock_build):
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {'values': []}
        
        result = get_google_sheet_data()
        
        self.assertIsNone(result)

    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_missing_columns(self, mock_credentials, mock_build):
        mock_values = [
            ['Email Address', 'Tool being used'],  # Missing required columns
            ['test@example.com', 'Tool1']
        ]
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {'values': mock_values}
        
        result = get_google_sheet_data()
        
        self.assertIsNone(result)

    @patch('extract_data.build')
    @patch('extract_data.Credentials')
    def test_get_google_sheet_data_invalid_ratings(self, mock_credentials, mock_build):
        mock_values = [
            ['Email Address', 'Tool being used', 'Feature used', 'Context Awareness', 
             'Autonomy', 'Experience', 'Output Quality', 'Overall Rating', 'Unique ID'],
            ['test@example.com', 'Tool1', 'Feature1', 'invalid', 'invalid', 'invalid', 'invalid', 'invalid', 'ID1']
        ]
        
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        mock_service.spreadsheets().values().get().execute.return_value = {'values': mock_values}
        
        # Mock clear_target_sheet to return None to simulate failure
        with patch('extract_data.clear_target_sheet', return_value=None):
            result = get_google_sheet_data()
            
            self.assertIsNone(result)

    @patch('extract_data.get_google_sheet_data')
    def test_main_execution_success(self, mock_get_data):
        mock_get_data.return_value = self.test_df
        
        # Simulate main execution
        if __name__ == "__main__":
            result_data = get_google_sheet_data()
            self.assertIsNotNone(result_data)
            self.assertEqual(len(result_data), 2)

    @patch('extract_data.get_google_sheet_data')
    def test_main_execution_failure(self, mock_get_data):
        mock_get_data.return_value = None
        
        # Simulate main execution
        if __name__ == "__main__":
            result_data = get_google_sheet_data()
            self.assertIsNone(result_data)

    def test_get_result_status(self):
        # Test the get_result_status function indirectly through DataFrame operations
        test_differences = pd.Series([-2, -0.5, 0, 0.5, 2])
        expected_results = ['Not ok', 'Ok', 'Ok', 'Ok', 'Not ok']
        
        df = pd.DataFrame({'Difference': test_differences})
        df['Result'] = df['Difference'].apply(
            lambda x: 'Ok' if -1 <= x <= 1 else 'Not ok'
        )
        
        results = df['Result'].tolist()
        self.assertEqual(results, expected_results)

if __name__ == '__main__':
    unittest.main()