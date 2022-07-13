import requests
import json

MOSCOW_LAT = 55
MOSCOW_LON = 37

usr_lat = MOSCOW_LAT
usr_lon = MOSCOW_LON
usr_lang = 'ru_RU'

forecast_data = dict.fromkeys(['morning', 'day', 'evening', 'night'])
cond_description = json.load(
    open('weather_cond_description.json', 'r', encoding='utf-8'))


def get_forecast_text(days_from_now: int) -> str:
    payload = {'lat': usr_lat,
               'lon': usr_lon,
               'lang': usr_lang,
               'limit': days_from_now + 1}

    with open('yandex_weather_api_key.txt', 'r') as file:
        YANDEX_WEATHER_API_KEY = file.readline()
    YANDEX_WEATHER_REQUEST_URL = 'https://api.weather.yandex.ru/v2/forecast'
    weather_response = requests.get(YANDEX_WEATHER_REQUEST_URL,
                                    params=payload,
                                    headers={'X-Yandex-API-Key': YANDEX_WEATHER_API_KEY})

    parts_for_day = \
        weather_response.json()['forecasts'][days_from_now]['parts']

    forecast_message_greeting = \
        f"Привет! Вот прогноз погоды на \
        {weather_response.json()['forecasts'][days_from_now]['date']}:\n"

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
