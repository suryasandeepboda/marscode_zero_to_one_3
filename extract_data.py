from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import pandas as pd

def get_google_sheet_data():
    # Define the scope and credentials
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
    creds = Credentials.from_service_account_file('credentials.json', scopes=SCOPES)

    # Create the service
    service = build('sheets', 'v4', credentials=creds)

    # Spreadsheet ID from the URL
    SPREADSHEET_ID = '15FMeidgU2Dg7Q4JKPkLAdJmQ3IxWCWJXjhCo9UterCE'
    RANGE_NAME = 'POD 5!A1:CE1000'  # We'll fetch all columns and filter later

    try:
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME
        ).execute()

        values = result.get('values', [])
        
        if not values:
            print('No data found.')
            return None

        # Convert to DataFrame
        df = pd.DataFrame(values[1:], columns=values[0])  # First row as headers

        # Select required columns
        required_columns = [
            'Email address',
            'Tool used',
            'Feature Used',
            'Context Awareness',
            'Autonomy',
            'Experience',
            'Output Quality',
            'Overall Rating',
            'Unique ID',
            'Pod'
        ]

        # Filter only required columns
        filtered_df = df[required_columns]
        
        return filtered_df

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    data = get_google_sheet_data()
    if data is not None:
        print("Successfully retrieved data:")
        print(data.head())  # Display first 5 rows