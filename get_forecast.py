from loguru import logger

import requests
import os
from typing import Any

from user_types import UserType
from weather_objects_types import WeatherResponseType
from constants import YANDEX_API_HEADER, YANDEX_WEATHER_REQUEST_URL, USER_LANGUAGE
from constants import weather_condition_description
import exceptions




def get_forecast_from_API(user: UserType, up_to_days_from_now: int=1) -> Any:
    ''' Получает прогноз от api.weather.yandex.ru и возвращает объект с данными
    прогноза на up_to_days_from_now от текущего дня (не включительно).
    up_to_days_from_now - количество дней, включенных в прогноз, не считая текущего'''

    payload = {'lat': user.lat,
               'lon': user.lon,
               'lang': USER_LANGUAGE,
               'limit': up_to_days_from_now + 1}

    try:
        forecast_response = requests.get(YANDEX_WEATHER_REQUEST_URL,
                                        params=payload,
                                        headers=YANDEX_API_HEADER,
                                        timeout=10)
        forecast_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        logger.exception("Ошибка HTTP:")
        return None
    except requests.exceptions.RequestException as e:
        logger.exception("Ошибка соединения с сервером погоды:")
        return None
    else:
        logger.info(f"""Получен ответ на запрос {forecast_response.request.url} для пользователя {user.id} с координатами ({user.lat}, {user.lon}).""")
        return forecast_response.json()

     
def get_last_day_forecast_text(user: UserType, forecast_obj: WeatherResponseType) -> str:
    '''Возвращает текст прогноза для последнего дня, содержащегося в forecast_obj
    forecast_obj - объект с данными прогноза на один или несколько дней,
    полученный от api.weather.yandex.ru'''

    forecast_for_day = forecast_obj['forecasts'][-1]['parts']

    forecast_message_greeting = \
    f"""Привет! Вот прогноз погоды на {forecast_obj['forecasts'][-1]['date']}.\n\n""" \
    f"""Место: {forecast_obj['geo_object']['locality']['name']}\n\n"""

    forecast_message_morning = \
    f"Утро\n    Средняя температура: {forecast_for_day['morning']['temp_avg']}C\n \
    Ощущается как {forecast_for_day['morning']['feels_like']}C\n\
    {weather_condition_description[forecast_for_day['morning']['condition']]}\n\
    Скорость ветра: {forecast_for_day['morning']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {forecast_for_day['morning']['uv_index']}\n\n"

    forecast_message_day = \
    f"День\n    Средняя температура: {forecast_for_day['day']['temp_avg']}C\n\
    Ощущается как {forecast_for_day['day']['feels_like']}C\n\
    {weather_condition_description[forecast_for_day['day']['condition']]}\n\
    Скорость ветра: {forecast_for_day['day']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {forecast_for_day['day']['uv_index']}\n\n"

    forecast_message_evening = \
    f"Вечер\n    Средняя температура: {forecast_for_day['evening']['temp_avg']}C\n\
    Ощущается как {forecast_for_day['evening']['feels_like']}C\n\
    {weather_condition_description[forecast_for_day['evening']['condition']]}\n\
    Скорость ветра: {forecast_for_day['evening']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {forecast_for_day['evening']['uv_index']}\n\n"
    
    return forecast_message_greeting + \
            forecast_message_morning \
            + forecast_message_day \
            + forecast_message_evening


def get_forecast_for_day(user: UserType, days_from_now: int=1)->str:
    try:
        return get_last_day_forecast_text(user, get_forecast_from_API(user, days_from_now))
    except TypeError as e:
        logger.exception("Получен некорректный объект с данными о прогнозе:")
        return "Не удалось получить прогноз."
        