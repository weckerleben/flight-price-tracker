import logging as log
from datetime import datetime

from selenium import webdriver

from app.config import MAX_SEARCHES_BEFORE_RESTART, CYCLE_SLEEP_MIN, ROUND_TRIP
from app.database.connection import get_db_session
from app.database.repository.flight_repository import FlightRepository
from app.services.scraping_service import scrape_best_price
from app.utils.chrome_driver import configure_chrome_options
from app.utils.logger import configure_log
from app.utils.utils import countdown_timer, calculate_days_between_dates, build_url

configure_log()


def search_flights_round_trip(departure_month, start_day, end_day, return_range, origin_city, destination_city,
                              filters):
    search_count = 0
    cycle_count = 0

    chrome_options = configure_chrome_options()
    driver = webdriver.Chrome(options=chrome_options)

    for departure_day in range(start_day, end_day + 1):
        for return_day in return_range:
            if search_count >= MAX_SEARCHES_BEFORE_RESTART:
                log.info("Closing Chrome driver...")
                driver.quit()
                search_count = 0
                cycle_count += 1
                countdown_timer(CYCLE_SLEEP_MIN * 60)
                log.info("Starting Chrome driver...")
                driver = webdriver.Chrome(options=chrome_options)

            departure_date = f"2024-{departure_month}-{str(departure_day).zfill(2)}"
            return_date = f"2024-07-{return_day}"
            days = calculate_days_between_dates(departure_date, return_date)
            URL = build_url('kayak', departure_date, return_date, ROUND_TRIP, origin_city, destination_city, filters)
            if days > 30:
                price, duration = scrape_best_price(driver, URL)
                average_price_per_day = round(float(price) / days, 2)
                while not (price and duration):
                    price, duration = scrape_best_price(driver, URL)
                flight_data = {
                    'departure_date': datetime.strptime(departure_date, "%Y-%m-%d"),
                    'return_date': datetime.strptime(return_date, "%Y-%m-%d"),
                    'days_count': days,
                    'total_price': price,
                    'average_price_per_day': average_price_per_day,
                    'average_duration': duration,
                    'search_link': URL,
                }
                db_session = get_db_session()
                try:
                    flight_repo = FlightRepository(db_session)
                    flight_repo.insert_or_update_flight(flight_data)
                except Exception as e:
                    log.error(f"Error al insertar en la base de datos: {e}")
                    db_session.rollback()
                finally:
                    db_session.close()
            log.info(
                f"[{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]\t{departure_date}\t{return_date}\t{days}\t{price}\t{round(int(price) / days, 2)}\t{duration}\t")
            search_count += 1
            log.info(
                f"\t\t\t{search_count}/{MAX_SEARCHES_BEFORE_RESTART}")
    driver.quit()


def main():
    search_flights_round_trip('06', 14, 30, range(20, 32), 'ASU', 'FRA',
                              'sort=price_a&fs=cfc=1;price=-1800;legdur=-1500;stops=1;bfc=1')  # Junio
    search_flights_round_trip('07', 1, 15, range(20, 32), 'ASU', 'FRA',
                              'sort=price_a&fs=cfc=1;price=-1800;legdur=-1500;stops=1;bfc=1')  # Julio


if __name__ == '__main__':
    main()
