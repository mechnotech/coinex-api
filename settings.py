from dotenv import load_dotenv
import os

load_dotenv()

LOGGING = True

API_WAIT_TIME = 0.1
ACCESS_ID = os.getenv('ACCESS_ID')
SECRET_KEY = os.getenv('SECRET_KEY')

URL_API = 'https://api.coinex.com/v1/'
