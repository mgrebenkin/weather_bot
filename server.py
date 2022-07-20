from loguru import logger
logger.add('log/log.log', retention=1)

from aiogram import Bot, Dispatcher, executor, types
import aiogram
import aioschedule
import asyncio
import json
from dotenv import load_dotenv, find_dotenv
import os

import get_forecast
import exceptions

'''Получение токена бота из файла, подключение к API телеграма и инициализация диспетчера'''
load_dotenv(find_dotenv())

try:
    TG_BOT_API_TOKEN = os.getenv('TG_BOT_API_TOKEN')
    if TG_BOT_API_TOKEN is None: 
        raise exceptions.GettingEnvVarError('Не удалось получить токен бота.')
    bot = Bot(token=TG_BOT_API_TOKEN)
    dp = Dispatcher(bot)
except exceptions.GettingEnvVarError as e:
    print(f"Ошибка доступа к переменной окружения:\n{e}")
except Exception as e:
    logger.exception("Ошибка инициализации бота:")
else:
    logger.info("Бот инициализирован.")

try:
    username_white_list = json.load(
            open('username_white_list.json', 'r', encoding='utf-8'))
except OSError as e:
    logger.exception("Ошибка чтения файла:")

subscribers_for_daily_forecast = set()
DAILY_FORECAST_TIME = '20:00'
TASK_LOOP_PERIOD = 30  # seconds


def auth(func):

    async def wrapper(message):
        if message.from_user.username in username_white_list:
            return await message.reply("Нет доступа", reply=False)
        return await func(message)

    return wrapper


@dp.message_handler(commands=['start', 'help'])
@auth
async def greeting_reply(message: types.Message):
    await message.reply('Напиши /today для прогноза на сегодня и /tomorrow для прогноза на завтра.\n' +
        'Напиши /subscribe, чтобы подписаться на ежедневный и напиши /unsubscribe, чтобы отписаться.')


@dp.message_handler(commands=['today', 'tomorrow'])
@auth
async def forecast_answer(message: types.Message):
    if message.text == '/today':
        forecast_answer_text = get_forecast.get_forecast_for_day(0)
    elif message.text == '/tomorrow':
        forecast_answer_text = get_forecast.get_forecast_for_day(1)
    await message.answer(forecast_answer_text)


async def send_test_message(message: types.Message):
    await bot.send_message(message.from_user.id, f"Test {message.from_user.username}")


async def send_tomorrow_forecast(message: types.Message):
    await bot.send_message(message.from_user.id, get_forecast.get_forecast_for_day(1))


async def do_daily_forecasting(message: types.Message):

    job = aioschedule.every().day.at(DAILY_FORECAST_TIME).do(send_tomorrow_forecast, message=message)
    while message.from_user.username in subscribers_for_daily_forecast:
        await aioschedule.run_pending()
        await asyncio.sleep(TASK_LOOP_PERIOD)
    aioschedule.cancel_job(job)


@dp.message_handler(commands=['subscribe', 'sub'])
@auth
async def start_daily_forecasting(message: types.Message):
    subscribers_for_daily_forecast.add(message.from_user.username)
    await bot.send_message(message.from_user.id, f'Ты подписан на ежедневный прогноз в {DAILY_FORECAST_TIME}.')
    asyncio.create_task(do_daily_forecasting(message))


@dp.message_handler(commands=['unsubscribe', 'unsub'])
@auth
async def stop_daily_forecasting(message: types.Message):
    if message.from_user.username in subscribers_for_daily_forecast:
        subscribers_for_daily_forecast.discard(message.from_user.username)
        await bot.send_message(message.from_user.id, 'Ты отписан от ежедневного прогноза.')
    else:
        await bot.send_message(message.from_user.id, 'Ты не подписан на ежедневный прогноз.')



@dp.message_handler()
@auth
async def unknown_command_answer(message: types.Message):
    await message.reply('Напиши /today для прогноза на сегодня и /tomorrow для прогноза на завтра.\n' +
        'Напиши /subscribe или /sub чтобы подписаться на ежедневный и напиши /unsubscribe или /unsub, чтобы отписаться.')


async def startup_routine(_):
    logger.info("Бот авторизован и запущен.")


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=startup_routine)
    except aiogram.utils.exceptions.Unauthorized as e:
        logger.exception("Не удалось авторизовать бота:\n")
    