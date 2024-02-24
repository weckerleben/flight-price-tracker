import logging
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from src.config import SERVICE_ACCOUNT_FILE, SCOPES, SPREADSHEET_ID
from src.logger import configure_logging

configure_logging()


def get_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds, cache_discovery=False)
    return service


def update_data_in_sheet(range_name, values):
    service = get_service()
    body = {
        'values': values,
        'majorDimension': 'ROWS'
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()
    logging.info(f"{result.get('updatedCells')} cells updated.")


def read_value_from_sheet(cell_range):
    service = get_service()
    result = service.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=cell_range
    ).execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
        return None
    else:
        return values[0][0]


def compare_and_update_sheet(departure_date, return_date, days, scraped_price, duration, URL):
    current_price_str = read_value_from_sheet('Kayak!E1') if read_value_from_sheet('Kayak!E1') is not None else '9999'
    current_price_per_day_str = read_value_from_sheet('Kayak!F2') if read_value_from_sheet('Kayak!F2') is not None else '9999'
    try:
        if scraped_price is not None:
            current_price = float(current_price_str)
            scraped_price_float = float(scraped_price)
            current_price_per_day = float(current_price_per_day_str.replace(',', '.'))
            price_per_day = round(scraped_price_float / days, 2)

            if scraped_price_float < current_price:
                logging.info(f"New lowest new price found: {scraped_price_float}. Updating sheet...")
                values = [
                    [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), departure_date, return_date, days, scraped_price,
                     price_per_day, duration, URL]]
                update_data_in_sheet('Kayak!A1', values)

            if price_per_day < current_price_per_day and price_per_day is not None:
                logging.info(
                    f"New lowest new price per day found: {price_per_day}, before {current_price_per_day}. Updating sheet...")
                values = [
                    [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), departure_date, return_date, days, scraped_price,
                     price_per_day, duration, URL]]
                update_data_in_sheet('Kayak!A2', values)
    except:
        pass
