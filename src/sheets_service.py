import logging
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from src.config import SERVICE_ACCOUNT_FILE, SCOPES, SPREADSHEET_ID
from src.logger import configure_logging

configure_logging()


def get_service():
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    service = build('sheets', 'v4', credentials=creds)
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
        return values[0][0]  # Devuelve el valor de la celda C1


def compare_and_update_sheet(departure_date, return_date, scraped_price, duration, URL):
    current_price_str = read_value_from_sheet('Kayak!C1')
    try:
        # Intenta convertir el precio leído a un número flotante para la comparación
        current_price = float(current_price_str)
        scraped_price_float = float(scraped_price)

        # Si el precio obtenido del scraping es menor, actualiza la hoja
        if scraped_price_float < current_price and scraped_price != 0:
            logging.info(f"Nuevo precio menor encontrado: {scraped_price_float}. Actualizando hoja...")
            values = [[departure_date, return_date, scraped_price, duration, URL,
                       datetime.now().strftime("%d/%m/%Y %H:%M:%S")]]
            update_data_in_sheet('Kayak!A1', values)  # Asume que quieres sobrescribir desde A1
    except ValueError:
        logging.error(
            f"Error al convertir precios para comparación. Precio actual: {current_price_str}, Precio de scraping: {scraped_price}")
