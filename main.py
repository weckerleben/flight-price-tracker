import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

logging.basicConfig(filename='prices.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SERVICE_ACCOUNT_FILE = 'gsheets-394012-45373b59d14d.json'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

SPREADSHEET_ID = '1NfWHYqeQ0K6Wj8O6m6tjeiC4oRJyQl9S7TJ_p5eG_OQ'

with open('prices.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Opcionalmente, escribe los encabezados de las columnas
    writer.writerow(['Departure Date', 'Return Date', 'Price', 'Duration'])


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
            values = [[departure_date, return_date, scraped_price, duration, URL]]
            update_data_in_sheet('Kayak!A1', values)  # Asume que quieres sobrescribir desde A1
    except ValueError:
        logging.error(f"Error al convertir precios para comparación. Precio actual: {current_price_str}, Precio de scraping: {scraped_price}")


def write_price_to_csv(departure_date, return_date, price, duration):
    with open('prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([departure_date, return_date, price, duration])


def configure_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('start-maximized')
    chrome_options.add_argument('disable-infobars')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--blink-settings=imagesEnabled=true')  # Deshabilitar imágenes
    return chrome_options


def build_url(airline, go_date, back_date):
    base_urls = {
        'latam': 'https://www.latamairlines.com/py/es/ofertas-vuelos/?origin=ASU&destination=FRA&adt=1&chd=0&inf=0&trip=RT&cabin=Economy&redemption=false&sort=PRICE%2Casc',
        'skyscanner': 'https://www.espanol.skyscanner.com/transporte/vuelos/asu/fra',
        'kayak': 'https://www.kayak.com/flights/ASU-FRA'
    }

    if airline == 'kayak':
        return f"{base_urls[airline]}/{go_date}/{back_date}?sort=price_a&fs=cfc=1;price=-1800;legdur=-1500;stops=1"
    else:
        raise ValueError("Airline not supported")


def wait_for_at_least_n_elements_and_no_captcha(driver, css_selector, n, timeout=10):
    class CombinedCondition:
        """Define a combined condition for WebDriverWait."""
        def __call__(self, driver):
            elements = driver.find_elements(By.CSS_SELECTOR, css_selector)
            captcha_present = len(driver.find_elements(By.CSS_SELECTOR, ".WZTU-captcha")) > 0
            return len(elements) >= n and not captcha_present

    WebDriverWait(driver, timeout).until(CombinedCondition())


def scrape_best_price(driver, URL):
    try:
        driver.get(URL)
        wait_for_at_least_n_elements_and_no_captcha(driver, ".nrc6", 1, timeout=10)
        time.sleep(5)  # Considerar ajustar o eliminar este sleep si no es necesario
        recommended_price_element = driver.find_element(By.CSS_SELECTOR, '[data-content="price_a"]')
        recommended_price = recommended_price_element.text.replace('Cheapest', '').replace('\n', '')
        price = recommended_price.split(' • ')[0].replace('$', '').replace(',', '') if recommended_price else ""
        duration = recommended_price.split(' • ')[1].replace('h ', ':').replace('m', '') if recommended_price else ""
        return price, duration
    except TimeoutException:
        return 0, "00:00"


def search_flights(departure_month, start_day, end_day, return_range):
    chrome_options = configure_chrome_options()
    with webdriver.Chrome(options=chrome_options) as driver:
        for departure_day in range(start_day, end_day + 1):
            for return_day in return_range:
                departure_date = f"2024-{departure_month}-{str(departure_day).zfill(2)}"
                return_date = f"2024-07-{return_day}"
                URL = build_url('kayak', departure_date, return_date)
                price, duration = scrape_best_price(driver, URL)
                compare_and_update_sheet(departure_date, return_date, price, duration, URL)
                write_price_to_csv(departure_date, return_date, price, duration)
                print(f"{departure_date}, {return_date}, {price}, {duration}")
                if not price:
                    logging.info(f"No se encontró precio para la fecha de salida {str(departure_day).zfill(2)}/{departure_month} y regreso {return_day}/07")
                time.sleep(random.uniform(1, 3))  # Reducir tiempo de espera


def main():
    search_flights('06', 1, 30, range(20, 32))  # Junio
    search_flights('07', 1, 15, range(20, 32))  # Julio


if __name__ == '__main__':
    main()
