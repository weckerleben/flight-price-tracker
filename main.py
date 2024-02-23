import csv
import logging
import random
import time
from datetime import datetime

from selenium import webdriver

from src.chrome_driver import configure_chrome_options
from src.logger import configure_logging
from src.scraping import scrape_best_price
from src.sheets_service import compare_and_update_sheet
from src.utils import build_url

configure_logging()

with open('prices.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Opcionalmente, escribe los encabezados de las columnas
    writer.writerow(['Departure Date', 'Return Date', 'Price', 'Duration'])


def write_price_to_csv(departure_date, return_date, price, duration):
    with open('prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([departure_date, return_date, price, duration])


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
                print(
                    f"{departure_date}\t{return_date}\t{price}\t{duration}\t{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
                if not price:
                    logging.info(
                        f"No se encontró precio para la fecha de salida {str(departure_day).zfill(2)}/{departure_month} y regreso {return_day}/07")
                time.sleep(random.uniform(1, 3))  # Reducir tiempo de espera


def main():
    search_flights('06', 1, 30, range(20, 32))  # Junio
    search_flights('07', 1, 15, range(20, 32))  # Julio


if __name__ == '__main__':
    main()
