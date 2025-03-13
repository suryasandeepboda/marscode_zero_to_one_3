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
logger = logging.getLogger(__name__)

def get_google_sheet_data():
    try:
        # Define the scope and credentials
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
        creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)
        logger.info("Successfully loaded credentials")

        # Create the service
        service = build('sheets', 'v4', credentials=creds)
        logger.info("Successfully created Google Sheets service")

        # Spreadsheet ID from the URL
        SPREADSHEET_ID = '15FMeidgU2Dg7Q4JKPkLAdJmQ3IxWCWJXjhCo9UterCE'
        RANGE_NAME = 'POD 5!A1:CE1000'

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = result.get('values', [])
        
        if not values:
            logger.error('No data found in the sheet')
            return None

        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])
        logger.info(f"Retrieved {len(df)} rows of data")

        # Log available columns for debugging
        logger.debug(f"Available columns in sheet: {list(df.columns)}")

        # Map the required columns to actual column names in the sheet
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

        # Select required columns with flexible naming
        required_columns = []
        for sheet_col, mapped_col in column_mapping.items():
            if sheet_col in df.columns:
                df[mapped_col] = df[sheet_col]
                required_columns.append(mapped_col)
            else:
                logger.warning(f"Column '{sheet_col}' not found in sheet")

        # Filter only required columns
        filtered_df = df[required_columns]
        logger.info("Successfully filtered required columns")
        
        return filtered_df

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return None

if __name__ == "__main__":
    data = get_google_sheet_data()
    if data is not None:
        logger.info("Data retrieval successful")
        print("\nFirst 5 rows of retrieved data:")
        print(data.head())
    else:
        logger.error("Failed to retrieve data")