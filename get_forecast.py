import requests
import json

MOSCOW_LAT = 55
MOSCOW_LON = 37

usr_lat = MOSCOW_LAT
usr_lon = MOSCOW_LON
usr_lang = 'ru_RU'

forecast_data = dict.fromkeys(['morning', 'day', 'evening', 'night'])
cond_description = {
'clear': 'Ясно',
'partly-cloudy': 'Малооблачно',
'cloudy': 'Облачно с прояснениями',
'overcast': 'Пасмурно',
'drizzle': 'Морось',
'light-rain': 'Небольшой дождь',
'rain': 'Дождь',
'moderate-rain': 'Умеренно сильный дождь',
'heavy-rain': 'Сильный дождь',
'continuous-heavy-rain': 'Длительный сильный дождь',
'showers': 'Ливень',
'wet-snow': 'Дождь со снегом',
'light-snow': 'Небольшой снег',
'snow': 'Снег',
'snow-showers': 'Снегопад',
'hail': 'Град',
'thunderstorm': 'Гроза',
'thunderstorm-with-rain': 'Дождь с грозой',
'thunderstorm-with-hail': 'Гроза с градом'}

payload = {'lat':usr_lat, 'lon':usr_lon, 'lang':usr_lang, 'limit':1}
with open('yandex_weather_api_key.txt','r') as file:
    YANDEX_WEATHER_API_KEY = file.readline()
YANDEX_WEATHER_REQUEST_URL = 'https://api.weather.yandex.ru/v2/forecast'
weather_response = requests.get(YANDEX_WEATHER_REQUEST_URL, 
    params=payload, 
    headers={'X-Yandex-API-Key':YANDEX_WEATHER_API_KEY})
weather_response_json = weather_response.json()
with open('weather_response.json', 'w') as weather_response_file:
    json.dump(weather_response_json, weather_response_file, 
    ensure_ascii=False, sort_keys=True, indent=4)
parts_for_day = weather_response_json['forecasts'][0]['parts']

forecast_message_greeting = f"Привет! Вот прогноз погоды на {weather_response_json['forecasts'][0]['date']}:"
forecast_message_morning = \
f"Утро\nСредняя температура: {parts_for_day['morning']['temp_avg']} C\n \
Ощущается как {parts_for_day['morning']['feels_like']} C\n \
{cond_description[parts_for_day['morning']['condition']]}\n \
Скорость ветра: {parts_for_day['morning']['wind_speed']} м/с\n \
Индекс УФ-излучения: {parts_for_day['morning']['uv_index']}\n"

forecast_message_day = \
f"День\nСредняя температура: {parts_for_day['day']['temp_avg']} C\n \
Ощущается как {parts_for_day['day']['feels_like']} C\n \
{cond_description[parts_for_day['day']['condition']]}\n \
Скорость ветра: {parts_for_day['day']['wind_speed']} м/с\n \
Индекс УФ-излучения: {parts_for_day['day']['uv_index']}\n"

forecast_message_evening = \
f"Вечер\nСредняя температура: {parts_for_day['evening']['temp_avg']} C\n \
Ощущается как {parts_for_day['evening']['feels_like']} C\n \
{cond_description[parts_for_day['evening']['condition']]}\n \
Скорость ветра: {parts_for_day['evening']['wind_speed']} м/с\n \
Индекс УФ-излучения: {parts_for_day['evening']['uv_index']}\n"

print(forecast_message_greeting)
print(forecast_message_morning)
print(forecast_message_day)
print(forecast_message_evening)

'''Средняя температура
 ощущается как
 характер погоды
 скорость ветра
 индекс УФ'''
