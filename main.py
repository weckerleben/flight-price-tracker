import csv
import logging
import time
from datetime import datetime

from selenium import webdriver

from src.chrome_driver import configure_chrome_options
from src.logger import configure_logging
from src.scraping import scrape_best_price
from src.sheets_service import compare_and_update_sheet
from src.utils import build_url, calculate_days_between_dates

configure_logging()

with open('prices.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Opcionalmente, escribe los encabezados de las columnas
    writer.writerow(['Date Updated', 'Departure Date', 'Return Date', 'Days', 'Price', 'Duration', 'URL'])


def write_price_to_csv(departure_date, return_date, days, price, duration, URL):
    with open('data/prices.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(
            [datetime.now().strftime("%d/%m/%Y %H:%M:%S"), departure_date, return_date, days, price, duration, URL])


def search_flights(departure_month, start_day, end_day, return_range):
    search_count = 0
    cycle_count = 0
    max_searches_before_restart = [40, 20, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40, 40]

    chrome_options = configure_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    for departure_day in range(start_day, end_day + 1):
        for return_day in return_range:
            if search_count >= max_searches_before_restart[cycle_count]:
                logging.info("Closing Chrome driver...")
                driver.quit()
                search_count = 0
                cycle_count += 1
                logging.info("Waiting 2 minutes...")
                time.sleep(120)
                logging.info("Starting Chrome driver...")
                driver = webdriver.Chrome(options=chrome_options)

            departure_date = f"2024-{departure_month}-{str(departure_day).zfill(2)}"
            return_date = f"2024-07-{return_day}"
            days = calculate_days_between_dates(departure_date, return_date)
            URL = build_url('kayak', departure_date, return_date)
            price, duration = scrape_best_price(driver, URL)
            compare_and_update_sheet(departure_date, return_date, days, price, duration, URL)
            write_price_to_csv(departure_date, return_date, days, price, duration, URL)
            print(
                f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]\t{departure_date}\t{return_date}\t{price}\t{duration}\t")
            search_count += 1
            sleep_time = 4
            logging.info(
                f"{search_count}/{max_searches_before_restart[cycle_count]} - Sleeping {sleep_time} secs...")
            time.sleep(sleep_time)
    driver.quit()


def main():
    search_flights('06', 1, 30, range(20, 32))  # Junio
    search_flights('07', 1, 15, range(20, 32))  # Julio


if __name__ == '__main__':
    main()
