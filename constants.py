from loguru import logger
from dotenv import load_dotenv, find_dotenv
from os import getenv

import json
import exceptions


load_dotenv(find_dotenv())
try:
    TG_BOT_API_TOKEN = getenv('TG_BOT_API_TOKEN')
    if TG_BOT_API_TOKEN is None: 
        raise exceptions.GettingEnvVarError('Не удалось получить токен бота.')
    
    DB_PATH = getenv('DB_PATH')
    if DB_PATH is None:
        raise exceptions.GettingEnvVarError('Не удалось получить путь к базе данных пользователей')
    
    YANDEX_WEATHER_API_KEY = getenv('YANDEX_WEATHER_API_KEY')
    if YANDEX_WEATHER_API_KEY is None:
        raise exceptions.GettingEnvVarError('Не удалось получить API-ключ сервиса прогноза погоды')

    AUTH_ENABLED= getenv('ENABLE_AUTH', 'False').lower() in ['true', 't', '1', 'y', 'yes']
    if AUTH_ENABLED is None:
        raise exceptions.GettingEnvVarError("""Не удалось получить флаг включения авторизации. """ 
        """Авторизация по умолчанию отключена.""")

except exceptions.GettingEnvVarError:
    logger.exception("Ошибка доступа к переменной окружения:\n")

YANDEX_WEATHER_REQUEST_URL = 'https://api.weather.yandex.ru/v2/forecast'
YANDEX_API_HEADER = {'X-Yandex-API-Key': YANDEX_WEATHER_API_KEY}
USER_LANGUAGE = 'ru_RU'
DEFAULT_DAILY_FORECAST_TIME = '20:00'
TASK_LOOP_PERIOD = 30  # seconds

try:
    weather_condition_description = json.load(
            open('weather_cond_description.json', 'r', encoding='utf-8'))
    if AUTH_ENABLED:
        username_white_list = json.load(
                open('username_white_list.json', 'r', encoding='utf-8'))
    else:
        username_white_list=list()
except OSError:
    logger.exception("Ошибка чтения файла:")
    username_white_list=list()
