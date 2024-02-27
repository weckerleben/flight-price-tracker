import os
from dotenv import load_dotenv

# Carga las variables de entorno del archivo .env
load_dotenv()

SERVICE_ACCOUNT_FILE = os.getenv('SERVICE_ACCOUNT_FILE')
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
ONE_WAY = 'one_way'
ROUND_TRIP = 'round_trip'
CYCLE_SLEEP_MIN = int(os.getenv('CYCLE_SLEEP_MIN', 5))
SEARCH_SLEEP_SEC = int(os.getenv('SEARCH_SLEEP_SEC', 7))
MAX_SEARCHES_BEFORE_RESTART = int(os.getenv('MAX_SEARCHES_BEFORE_RESTART', 24))
DATABASE_URI = os.getenv('DATABASE_URI')
