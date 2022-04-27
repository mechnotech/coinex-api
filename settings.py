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
VERBOSITY = int(os.getenv('VERBOSITY', 0))

API_WAIT_TIME = float(os.getenv('API_WAIT_TIME', 0.07))
ACCESS_ID = os.getenv('ACCESS_ID')
SECRET_KEY = os.getenv('SECRET_KEY')
TICKER = os.getenv('TICKER')
BORDER_PRICE = float(os.getenv('BORDER_PRICE', 0.04))
DIRECTION = os.getenv('DIRECTION', 'buy')
TIMEOUT = 10.0
HIDDEN = True if os.getenv('HIDDEN') == True else False

URL_API = 'https://api.coinex.com/v1/'
