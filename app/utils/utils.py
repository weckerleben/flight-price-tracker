import logging as log
import time
from datetime import datetime

from app.config import ROUND_TRIP, ONE_WAY
from app.utils.logger import configure_log

configure_log()


def build_url(airline, go_date, back_date, trip_type, origin_city, destination_city, filters):
    base_urls = {
        'latam': 'https://www.latamairlines.com/py/es/ofertas-vuelos/?origin=ASU&destination=FRA&adt=1&chd=0&inf=0&trip=RT&cabin=Economy&redemption=false&sort=PRICE%2Casc',
        'skyscanner': 'https://www.espanol.skyscanner.com/transporte/vuelos/asu/fra',
        'kayak': f"https://www.kayak.com/flights/{origin_city}-{destination_city}"
    }
    if trip_type == ROUND_TRIP:
        if airline == 'kayak':
            return f"{base_urls[airline]}/{go_date}/{back_date}?{filters}"
        else:
            raise ValueError("Airline not supported")
    if trip_type == ONE_WAY:
        if airline == 'kayak':
            return f"{base_urls[airline]}/{go_date}?{filters}"
        else:
            raise ValueError("Airline not supported")


def calculate_days_between_dates(date1, date2):
    start_date = datetime.strptime(date1, '%Y-%m-%d').date()
    end_date = datetime.strptime(date2, '%Y-%m-%d').date()
    difference = end_date - start_date
    return difference.days


def countdown_timer(seconds):
    mins, secs = divmod(seconds, 60)
    time_format = '{:02d}:{:02d}'.format(mins, secs)
    log.info(f"Sleeping {time_format}...")
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        time_format = '{:02d}:{:02d}'.format(mins, secs)
        log.info(time_format)
        time.sleep(1)
        seconds -= 1
    log.info("00:00")  # Cuando el contador llega a 0, imprime 00:00


def log_no_flights_date(departure_date):
    with open('data/no_flights_found.csv', 'a') as file:
        file.write(departure_date + '\n')


def read_no_flights_dates():
    try:
        with open('data/no_flights_found.csv', 'r') as file:
            return file.read().splitlines()
    except FileNotFoundError:
        return []
