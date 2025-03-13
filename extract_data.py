"""
Module for extracting data from Google Sheets using Google Sheets API.
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import logging
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
LOGGER = logging.getLogger(__name__)

def clear_target_sheet():
    """Clear the target spreadsheet"""
    try:
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
        service = build('sheets', 'v4', credentials=creds)
        
        target_spreadsheet_id = '1FEqiDqqPfb9YHAWBiqVepmmXj22zNqXNNI7NLGCDVak'
        range_name = 'Sheet1!A:Z'  # Clear all columns
        
        clear_request = service.spreadsheets().values().clear(
            spreadsheetId=target_spreadsheet_id,
            range=range_name
        )
        clear_request.execute()
        LOGGER.info("Target sheet cleared successfully")
        return service
    except Exception as error:
        LOGGER.error("Error clearing target sheet: %s", str(error))
        return None

def write_to_target_sheet(df, service):
    """Write data to target sheet with formatting"""
    try:
        target_spreadsheet_id = '1FEqiDqqPfb9YHAWBiqVepmmXj22zNqXNNI7NLGCDVak'
        
        # Prepare data for writing
        headers = df.columns.tolist()
        values = [headers] + df.values.tolist()
        
        # Write data
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=target_spreadsheet_id,
            range='Sheet1!A1',
            valueInputOption='RAW',
            body=body
        ).execute()
        
        # Apply conditional formatting for Result column
        result_column_index = headers.index('Result')
        requests = [{
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': 0,
                        'startRowIndex': 1,
                        'startColumnIndex': result_column_index,
                        'endColumnIndex': result_column_index + 1
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [{'userEnteredValue': 'Ok'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 0.0, 'green': 1.0, 'blue': 0.0}
                        }
                    }
                }
            }
        }, {
            'addConditionalFormatRule': {
                'rule': {
                    'ranges': [{
                        'sheetId': 0,
                        'startRowIndex': 1,
                        'startColumnIndex': result_column_index,
                        'endColumnIndex': result_column_index + 1
                    }],
                    'booleanRule': {
                        'condition': {
                            'type': 'TEXT_EQ',
                            'values': [{'userEnteredValue': 'Not ok'}]
                        },
                        'format': {
                            'backgroundColor': {'red': 1.0, 'green': 0.0, 'blue': 0.0}
                        }
                    }
                }
            }
        }]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=target_spreadsheet_id,
            body={'requests': requests}
        ).execute()
        
        LOGGER.info("Data written to target sheet successfully")
        return True
    except Exception as error:
        LOGGER.error("Error writing to target sheet: %s", str(error))
        return False

def get_google_sheet_data():
    """
    Retrieves and processes data from a Google Sheet.
    
    Returns:
        pandas.DataFrame: Processed data from the sheet, or None if an error occurs
    """
    try:
        # Define the scope and credentials
        scopes = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
        LOGGER.info("Successfully loaded credentials")

        # Create the service
        service = build('sheets', 'v4', credentials=creds)
        LOGGER.info("Successfully created Google Sheets service")

        # Spreadsheet constants
        spreadsheet_id = '15FMeidgU2Dg7Q4JKPkLAdJmQ3IxWCWJXjhCo9UterCE'
        range_name = 'POD 5!A1:CE1000'

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=range_name
        ).execute()

        values = result.get('values', [])
        
        if not values:
            LOGGER.error('No data found in the sheet')
            return None

        # Convert to DataFrame
        df_data = pd.DataFrame(values[1:], columns=values[0])
        LOGGER.info("Retrieved %d rows of data", len(df_data))

        # Log available columns for debugging
        LOGGER.info("Available columns in sheet: %s", list(df_data.columns))

        # Column mapping configuration
        column_mapping = {
            'Email Address': 'Email Address',
            'Tool being used': 'Tool being used',
            'Feature used': 'Feature used',
            'Context Awareness': 'Context Awareness',
            'Autonomy': 'Autonomy',
            'Experience': 'Experience',
            'Output Quality': 'Output Quality',
            'Overall Rating': 'Overall Rating',
            'Unique ID': 'Unique ID'
        }

        # Process columns
        required_columns = []
        for sheet_col, mapped_col in column_mapping.items():
            if sheet_col in df_data.columns:
                df_data[mapped_col] = df_data[sheet_col]
                required_columns.append(mapped_col)
            else:
                LOGGER.warning("Column '%s' not found in sheet", sheet_col)

        # Filter columns
        filtered_df = df_data[required_columns]
        LOGGER.info("Successfully filtered required columns")
        
        # After getting filtered_df, add calculations
        rating_columns = ['Context Awareness', 'Autonomy', 'Experience', 'Output Quality']
        
        # Convert rating columns to numeric
        for col in rating_columns + ['Overall Rating']:
            filtered_df[col] = pd.to_numeric(filtered_df[col], errors='coerce')

        # Calculate Mean Rating
        filtered_df['Mean Rating'] = filtered_df[rating_columns].mean(axis=1)
        LOGGER.info("Calculated mean ratings")

        # Calculate difference
        filtered_df['Difference'] = filtered_df['Mean Rating'] - filtered_df['Overall Rating']
        
        # Determine Result status
        def get_result_status(difference):
            if -1 <= difference <= 1:
                return 'Ok'
            return 'Not ok'
        
        filtered_df['Result'] = filtered_df['Difference'].apply(get_result_status)
        
        # Create color mapping for results
        filtered_df['Result_Color'] = filtered_df['Result'].map({
            'Ok': 'green',
            'Not ok': 'red'
        })
        
        LOGGER.info("Calculated results and color mapping")
        
        # Reorder columns
        final_columns = [
            'Email Address', 'Tool being used', 'Feature used',
            'Context Awareness', 'Autonomy', 'Experience', 'Output Quality',
            'Overall Rating', 'Mean Rating', 'Difference', 'Result',
            'Unique ID'
        ]
        
        filtered_df = filtered_df[final_columns]
        
        return filtered_df

    except Exception as error:
        LOGGER.error("An error occurred: %s", str(error), exc_info=True)
        return None

if __name__ == "__main__":
    result_data = get_google_sheet_data()
    if result_data is not None:
        LOGGER.info("Data retrieval successful")
        print("\nFirst 5 rows of retrieved data:")
        pd.set_option('display.max_columns', None)  # Show all columns
        print(result_data.head())
        
        # Print summary statistics
        print("\nSummary Statistics:")
        print(f"Total Records: {len(result_data)}")
        print(f"Ok Results: {len(result_data[result_data['Result'] == 'Ok'])}")
        print(f"Not Ok Results: {len(result_data[result_data['Result'] == 'Not ok'])}")
    else:
        LOGGER.error("Failed to retrieve data")