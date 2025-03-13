"""
Module for extracting data from Google Sheets using Google Sheets API.
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd
import logging

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
        LOGGER.debug("Available columns in sheet: %s", list(df_data.columns))

        # Column mapping configuration
        column_mapping = {
            'Email Address': 'Email address',
            'Tool Used': 'Tool being used',
            'Feature': 'Feature used',
            'Context Awareness Rating': 'Context Awareness',
            'Autonomy Rating': 'Autonomy',
            'Experience Rating': 'Experience',
            'Output Quality Rating': 'Output Quality',
            'Overall Satisfaction': 'Overall Rating',
            'Unique ID': 'Unique ID',
            'POD': 'Pod'
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
        
        return filtered_df

    except Exception as error:
        LOGGER.error("An error occurred: %s", str(error), exc_info=True)
        return None

if __name__ == "__main__":
    result_data = get_google_sheet_data()
    if result_data is not None:
        LOGGER.info("Data retrieval successful")
        print("\nFirst 5 rows of retrieved data:")
        print(result_data.head())
    else:
        LOGGER.error("Failed to retrieve data")