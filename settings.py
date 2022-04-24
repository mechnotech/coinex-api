import logging

from dotenv import load_dotenv
import os

load_dotenv()

VERBOSITY_LEVELS = {
    0: logging.WARNING,
    1: logging.INFO,
    2: logging.DEBUG
}
LOGGING = True
DEBUG = False
VERBOSITY = 0

API_WAIT_TIME = 0.11
ACCESS_ID = os.getenv('ACCESS_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
TICKER = os.getenv('TICKER')
BORDER_PRICE = float(os.getenv('MIN_PRICE', 0.04))
DIRECTION = os.getenv('DIRECTION', 'sell')
TIMEOUT = 10.0

URL_API = 'https://api.coinex.com/v1/'
