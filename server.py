from __future__ import annotations
from loguru import logger

from aiogram import Bot, Dispatcher, executor, types
import aiogram
import aioschedule
import asyncio
import json
from dotenv import load_dotenv, find_dotenv
import os
import time

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import fsm_storage

import get_forecast
import exceptions
from user_types import UserType
import keyboards

logger.add('log/log.log', retention=1)

"""Получение токена бота из файла, подключение к API телеграма и инициализация диспетчера"""
load_dotenv(find_dotenv())

try:
    TG_BOT_API_TOKEN = os.getenv('TG_BOT_API_TOKEN')
    if TG_BOT_API_TOKEN is None: 
        raise exceptions.GettingEnvVarError('Не удалось получить токен бота.')
    bot = Bot(token=TG_BOT_API_TOKEN)
    
    DB_PATH = os.getenv('DB_PATH')
    if DB_PATH is None:
        raise exceptions.GettingEnvVarError('Не удалось получить путь к базе данных пользователей')
    
    try:
        storage = fsm_storage.FSMStorage(DB_PATH)
    except Exception as e:
        logger.exception("Ошибка при создании списка подписанных пользователей:")
    else:
        logger.info('Установлено соединение с базой данных и получен список пользователей.')
    dp = Dispatcher(bot, storage=storage)

except exceptions.GettingEnvVarError as e:
    logger.exception("Ошибка доступа к переменной окружения:")
except Exception as e:
    logger.exception("Ошибка инициализации бота:")
else:
    logger.info("Бот инициализирован.")

try:
    username_white_list = json.load(
            open('username_white_list.json', 'r', encoding='utf-8'))
except OSError as e:
    logger.exception("Ошибка чтения файла:")

assigned_jobs: dict[int, aioschedule.Job] = dict()
DEFAULT_DAILY_FORECAST_TIME = '15:31'
TASK_LOOP_PERIOD = 30  # seconds


class FSMMain(StatesGroup):
    user_sent_location = State()
    user_subscribed = State()


def auth(func):

    async def wrapper(message: types.Message, state: FSMContext):
        if message.from_user.username in username_white_list:
            return await message.reply("Нет доступа", reply=False)
        return await func(message, state)

    return wrapper


@dp.message_handler(content_types=types.ContentType.LOCATION)
@auth
async def write_user_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['lat'] = message.location.latitude
        data['lon'] = message.location.longitude
    if await state.get_state() is None:
        await FSMMain.user_sent_location.set()
        await bot.send_message(message.from_user.id, """Теперь ты можешь получать прогноз погоды """ 
        """для места, где ты находишься""", reply_markup=keyboards.main_markup)
    else:
        await bot.send_message(message.from_user.id, """Твоя геопозиция обновлена.""", 
                                    reply_markup=keyboards.main_markup)


@dp.message_handler(state=None)
@auth
async def start(message: types.Message, state: FSMContext):
    await message.reply('Пришли свою геопозицию.', reply_markup=keyboards.request_location_markup)


@dp.message_handler(commands=['start', 'help'], state=FSMMain.all_states)
@auth
async def help_reply(message: types.Message, state: FSMContext):
    await message.reply('Напиши /today для прогноза на сегодня и /tomorrow для прогноза на завтра.\n' +
        'Напиши /subscribe, чтобы подписаться на ежедневный прогноз и напиши /unsubscribe, чтобы отписаться.', 
        reply_markup=keyboards.main_markup)


@dp.message_handler(commands=['today', 'tomorrow'], 
    state = [FSMMain.user_sent_location, FSMMain.user_subscribed])
@auth
async def forecast_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = UserType(
            id=state.user, lat=data['lat'], lon=data['lon'], 
            sending_time=data['sending_time'])
        forecast_answer_text = get_forecast.get_forecast_for_day(
            user, 0 if message.text == '/today' else 1)
    await message.answer(forecast_answer_text)


async def send_test_message(user: UserType):
    await bot.send_message(user.id, 
    f"Test {user.parameters.name} - {time.localtime().tm_min}:{time.localtime().tm_sec}")


async def send_tomorrow_forecast(user: UserType):
    await bot.send_message(user.id, get_forecast.get_forecast_for_day(user, 1))


async def do_daily_forecasting():
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(TASK_LOOP_PERIOD)
        

@dp.message_handler(commands=['subscribe', 'sub'], state=FSMMain.user_sent_location)
@auth
async def start_daily_forecasting(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sending_time'] = DEFAULT_DAILY_FORECAST_TIME
        subscriber = UserType(
            id=state.user, lat=data['lat'], lon=data['lon'], 
            sending_time=data['sending_time'])
        assigned_jobs[subscriber.id] = \
            aioschedule.every().day.at(data['sending_time']).do(
                send_tomorrow_forecast, 
                user=subscriber)
        logger.info(f"""Запущена новая рассылка по подписке для пользователя {subscriber}.""")
        await FSMMain.user_subscribed.set()
        await bot.send_message(
            message.from_user.id, 
            f"""Ты подписан на ежедневный прогноз в {data['sending_time']}.""")


@dp.message_handler(commands=['subscribe', 'sub'], state=FSMMain.user_subscribed)
@auth
async def start_daily_forecasting(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Ты уже подписан на ежедневный прогноз.")


@dp.message_handler(commands=['unsubscribe', 'unsub'], state=FSMMain.user_subscribed)
@auth
async def stop_daily_forecasting(message: types.Message, state: FSMContext):
    aioschedule.cancel_job(assigned_jobs.pop(message.from_user.id, None))
    logger.info(f"""Прекращена рассылка по подписке для пользователя c id {message.from_user.id}.""")
    await FSMMain.user_sent_location.set()  
    await bot.send_message(message.from_user.id, """Ты отписан от ежедневного прогноза.""")


@dp.message_handler(commands=['unsubscribe', 'unsub'], state=FSMMain.user_sent_location)
@auth
async def stop_daily_forecasting(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, """Ты не подписан на ежедневный прогноз.""")


@dp.message_handler()
@auth
async def unknown_command_answer(message: types.Message):
    await message.reply('Напиши /today для прогноза на сегодня и /tomorrow для прогноза на завтра.\n' +
        'Напиши /subscribe или /sub чтобы подписаться на ежедневный и напиши /unsubscribe или /unsub, чтобы отписаться.')


async def startup_routine(_):
    subscribers_set = await storage.get_subscribers_set()
    for subscriber in subscribers_set:
        assigned_jobs[subscriber.id] = \
            aioschedule.every().day.at(subscriber.sending_time).do(
                send_tomorrow_forecast, 
                user=subscriber)
        logger.info(f"""На старте запущена рассылка для пользователя {subscriber}.""")

    asyncio.create_task(do_daily_forecasting())
    logger.info("Бот авторизован и запущен.")


if __name__ == '__main__':
    try:
        executor.start_polling(dp, skip_updates=True, on_startup=startup_routine)
    except aiogram.utils.exceptions.Unauthorized as e:
        logger.exception("Не удалось авторизовать бота:\n")
