import requests
import json
import os
from typing import Any

from weather_objects_types import WeatherResponseType
import exceptions


MOSCOW_LAT = 55
MOSCOW_LON = 37

usr_lat = MOSCOW_LAT
usr_lon = MOSCOW_LON
usr_lang = 'ru_RU'


try:
    cond_description = json.load(
            open('weather_cond_description.json', 'r', encoding='utf-8'))
except OSError as e:
    print(f"Ошибка чтения файла {e.filename}:\n {e.strerror}")


def get_forecast_from_API(up_to_days_from_now: int=1) -> Any:
    ''' Получает прогноз от api.weather.yandex.ru и возвращает объект с данными
    прогноза на up_to_days_from_now от текущего дня (не включительно).
    up_to_days_from_now - количество дней, включенных в прогноз, не считая текущего'''

    try:
        YANDEX_WEATHER_API_KEY = os.getenv('YANDEX_WEATHER_API_KEY')
        if YANDEX_WEATHER_API_KEY is None:
            raise exceptions.GettingEnvVarError('Не удалось получить API-ключ сервиса прогноза погоды') 
    except exceptions.GettingEnvVarError as e:
        print(f"Ошибка доступа к переменной окружения:\n{e}")
    payload = {'lat': usr_lat,
               'lon': usr_lon,
               'lang': usr_lang,
               'limit': up_to_days_from_now + 1}

    YANDEX_WEATHER_REQUEST_URL = 'https://api.weather.yandex.ru/v2/forecast'
    try:
        forecast_response = requests.get(YANDEX_WEATHER_REQUEST_URL,
                                        params=payload,
                                        headers={'X-Yandex-API-Key': YANDEX_WEATHER_API_KEY},
                                        timeout=10)
        forecast_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP:\n{e.strerror}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с сервером погоды:\n{e.strerror}")
        return None
    else:
        return forecast_response.json()

     
def get_last_day_forecast_text(forecast_obj: WeatherResponseType) -> str:
    '''Возвращает текст прогноза для последнего дня, содержащегося в forecast_obj
    forecast_obj - объект с данными прогноза на один или несколько дней,
    полученный от api.weather.yandex.ru'''

    forecast_for_day = forecast_obj['forecasts'][-1]['parts']

    forecast_message_greeting = \
        "Привет! Вот прогноз погоды на " + \
        f"{forecast_obj['forecasts'][-1]['date']}:\n"

    forecast_message_morning = \
    f"Утро\n    Средняя температура: {forecast_for_day['morning']['temp_avg']}C\n\
    Ощущается как {forecast_for_day['morning']['feels_like']}C\n\
    {cond_description[forecast_for_day['morning']['condition']]}\n\
    Скорость ветра: {forecast_for_day['morning']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {forecast_for_day['morning']['uv_index']}\n\n"

    forecast_message_day = \
    f"День\n    Средняя температура: {forecast_for_day['day']['temp_avg']}C\n\
    Ощущается как {forecast_for_day['day']['feels_like']}C\n\
    {cond_description[forecast_for_day['day']['condition']]}\n\
    Скорость ветра: {forecast_for_day['day']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {forecast_for_day['day']['uv_index']}\n\n"

    forecast_message_evening = \
    f"Вечер\n    Средняя температура: {forecast_for_day['evening']['temp_avg']}C\n\
    Ощущается как {forecast_for_day['evening']['feels_like']}C\n\
    {cond_description[forecast_for_day['evening']['condition']]}\n\
    Скорость ветра: {forecast_for_day['evening']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {forecast_for_day['evening']['uv_index']}\n\n"
    
    return forecast_message_greeting + \
            forecast_message_morning \
            + forecast_message_day \
            + forecast_message_evening


def get_forecast_for_day(days_from_now: int)->str:
    try:
        return get_last_day_forecast_text(get_forecast_from_API(days_from_now))
    except TypeError as e:
        print(f'Получен некорректный объект с данными о прогнозе:\n{e}')
        return "Не удалось получить прогноз."
        