from __future__ import annotations
from loguru import logger

import aiogram, aioschedule, asyncio
from aiogram import Bot, Dispatcher, executor, types, filters
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

import time

from constants import TG_BOT_API_TOKEN, DB_PATH, TASK_LOOP_PERIOD, \
    DEFAULT_DAILY_FORECAST_TIME, AUTH_ENABLED
from constants import username_white_list
import fsm_storage
import get_forecast
import exceptions
from user_types import UserType
import keyboards

logger.add('log/log.log', retention=1)

"""Получение токена бота из файла, подключение к API телеграма и инициализация диспетчера"""

try:
    storage = fsm_storage.FSMStorage(DB_PATH)
except Exception:
    logger.exception("Ошибка при создании списка подписанных пользователей:")
else:
    logger.info('Установлено соединение с базой данных и получен список пользователей.')

try:
    bot = Bot(token=TG_BOT_API_TOKEN)
    dp = Dispatcher(bot, storage=storage)
except Exception:
    logger.exception("Ошибка инициализации бота:")
else:
    logger.info("Бот инициализирован.")

assigned_jobs: dict[int, aioschedule.Job] = dict()

class FSMMain(StatesGroup):
    user_sent_location = State()
    user_subscribed = State()


def auth(func):

    async def wrapper(message: types.Message, state: FSMContext):

        if not (message.from_user.username in username_white_list) and (AUTH_ENABLED):
            return await message.reply("Нет доступа", reply=False)
        return await func(message, state)

    return wrapper


@dp.message_handler(content_types=types.ContentType.LOCATION, state="*")
@auth
async def write_user_location(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['lat'] = message.location.latitude
        data['lon'] = message.location.longitude
        if await state.get_state() is None:
            await FSMMain.user_sent_location.set()
            await bot.send_message(message.from_user.id, """Теперь ты можешь получать прогноз погоды """ 
            """для места, где ты находишься. Пришли местоположение еще раз,"""
            """ чтобы обновить свое его.""", reply_markup=keyboards.main_markup)
        else:
            await bot.send_message(message.from_user.id, """Твое местоположение обновлено.""", 
                                        reply_markup=keyboards.main_markup)
            if await state.get_state() == FSMMain.user_subscribed.state:
                updated_user = UserType(
                    id=state.user, lat=message.location.latitude, lon=message.location.longitude, 
                    sending_time=data['sending_time'])
                assigned_jobs[str(message.from_user.id)].job_func.keywords['user'] = updated_user


@dp.message_handler(state=None)
@auth
async def start(message: types.Message, state: FSMContext):
    await message.reply('Пришли свое местоположение.', reply_markup=keyboards.request_location_markup)


@dp.message_handler(commands=['start', 'help', 'помощь'], state=FSMMain.all_states)
@auth
async def help_reply(message: types.Message, state: FSMContext):
    await message.reply(
        """Нажми нужную кнопку для прогноза на сегодня или на завтра.\n"""
        """Нажми кнопку "Подписаться", чтобы подписаться на ежедневный прогноз """
        """и "Отписаться", чтобы отписаться.\n"""
        """Ты можешь обновить свое местоположение, нажав соответствующую кнопку """
        """и отправив боту свою геопозицию.""",
        reply_markup=keyboards.main_markup)


@dp.message_handler(filters.Text(
        equals=['Прогноз на сегодня', 'Прогноз на завтра'], ignore_case=True), 
    state = [FSMMain.user_sent_location, FSMMain.user_subscribed])
@auth
async def forecast_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        user = UserType(
            id=state.user, lat=data['lat'], lon=data['lon'], 
            sending_time=data['sending_time'])
        forecast_answer_text = get_forecast.get_forecast_for_day(
            user, 0 if message.text == 'Прогноз на сегодня' else 1)
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
        

@dp.message_handler(filters.Text(
        equals=['Подписаться', 'sub'], ignore_case=True), 
    state=FSMMain.user_sent_location)
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


@dp.message_handler(filters.Text(
        equals=['Подписаться', 'sub'], ignore_case=True), 
    state=FSMMain.user_subscribed)
@auth
async def start_daily_forecasting(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, "Ты уже подписан на ежедневный прогноз.")


@dp.message_handler(filters.Text(
        equals=['Отписаться', 'unsub'], ignore_case=True), 
    state=FSMMain.user_subscribed)
@auth
async def stop_daily_forecasting(message: types.Message, state: FSMContext):
    aioschedule.cancel_job(assigned_jobs.pop(message.from_user.id, None))
    logger.info(f"""Прекращена рассылка по подписке для пользователя c id {message.from_user.id}.""")
    await FSMMain.user_sent_location.set()  
    await bot.send_message(message.from_user.id, """Ты отписан от ежедневного прогноза.""")


@dp.message_handler(filters.Text(
        equals=['Отписаться', 'unsub'], ignore_case=True),
    state=FSMMain.user_sent_location)
@auth
async def stop_daily_forecasting(message: types.Message, state: FSMContext):
    await bot.send_message(message.from_user.id, """Ты не подписан на ежедневный прогноз.""")


@dp.message_handler()
@auth
async def unknown_command_answer(message: types.Message):
    await message.reply(
        """Нажми нужную кнопку для прогноза на сегодня или на завтра.\n"""
        """Нажми кнопку "Подписаться", чтобы подписаться на ежедневный прогноз """
        """и "Отписаться", чтобы отписаться.\n"""
        """Ты можешь обновить свое местоположение, нажав соответствующую кнопку """
        """и отправив боту свою геопозицию.""",
        reply_markup=keyboards.main_markup)


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
