import requests
import json
import os

import exceptions


MOSCOW_LAT = 55
MOSCOW_LON = 37

usr_lat = MOSCOW_LAT
usr_lon = MOSCOW_LON
usr_lang = 'ru_RU'


forecast_data = dict.fromkeys(['morning', 'day', 'evening', 'night'])


def get_forecast_text(days_from_now: int) -> str:
    try:
        YANDEX_WEATHER_API_KEY = os.getenv('YANDEX_WEATHER_API_KEY')
        if YANDEX_WEATHER_API_KEY is None:
            raise exceptions.GettingEnvVarError('Не удалось получить API-ключ сервиса прогноза погоды')

        cond_description = json.load(
            open('weather_cond_description.json', 'r', encoding='utf-8'))
    except OSError as e:
        print(f"Ошибка чтения файла {e.filename}:\n {e.strerror}")
    except exceptions.GettingEnvVarError as e:
        print(e)
    payload = {'lat': usr_lat,
               'lon': usr_lon,
               'lang': usr_lang,
               'limit': days_from_now + 1}

    YANDEX_WEATHER_REQUEST_URL = 'https://api.weather.yandex.ru/v2/forecast'
    try:
        weather_response = requests.get(YANDEX_WEATHER_REQUEST_URL,
                                        params=payload,
                                        headers={'X-Yandex-API-Key': YANDEX_WEATHER_API_KEY},
                                        timeout=10)
        weather_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        print(f"Ошибка HTTP:\n{e.strerror}")
        return "Не удалось получить прогноз."
    except requests.exceptions.RequestException as e:
        print(f"Ошибка соединения с сервером погоды:\n{e.strerror}")
        return "Не удалось получить прогноз."   

    try:
        parts_for_day = \
            weather_response.json()['forecasts'][days_from_now]['parts']
    except LookupError as e:
        print("Отсутвует информация о нужном дне или JSON пустой.")
        return "Не удалось получить прогноз."

    forecast_message_greeting = \
        "Привет! Вот прогноз погоды на " + \
        f"{weather_response.json()['forecasts'][days_from_now]['date']}:\n"

    forecast_message_morning = \
    f"Утро\n    Средняя температура: {parts_for_day['morning']['temp_avg']}C\n\
    Ощущается как {parts_for_day['morning']['feels_like']}C\n\
    {cond_description[parts_for_day['morning']['condition']]}\n\
    Скорость ветра: {parts_for_day['morning']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {parts_for_day['morning']['uv_index']}\n\n"

    forecast_message_day = \
    f"День\n    Средняя температура: {parts_for_day['day']['temp_avg']}C\n\
    Ощущается как {parts_for_day['day']['feels_like']}C\n\
    {cond_description[parts_for_day['day']['condition']]}\n\
    Скорость ветра: {parts_for_day['day']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {parts_for_day['day']['uv_index']}\n\n"

    forecast_message_evening = \
    f"Вечер\n    Средняя температура: {parts_for_day['evening']['temp_avg']}C\n\
    Ощущается как {parts_for_day['evening']['feels_like']}C\n\
    {cond_description[parts_for_day['evening']['condition']]}\n\
    Скорость ветра: {parts_for_day['evening']['wind_speed']} м/с\n\
    Индекс УФ-излучения: {parts_for_day['evening']['uv_index']}\n\n"

    return forecast_message_greeting + \
        forecast_message_morning \
        + forecast_message_day \
        + forecast_message_evening


if __name__ == '__main__':
    print(get_forecast_text(1))
