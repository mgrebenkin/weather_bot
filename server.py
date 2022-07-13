from aiogram import Bot, Dispatcher, executor, types
import json
import get_forecast

with open('TG_BOT_API_TOKEN.txt', 'r') as file:
    TG_BOT_API_TOKEN = file.readline()

username_white_list = json.load(
    open('username_white_list.json', 'r', encoding='utf-8'))

bot = Bot(token=TG_BOT_API_TOKEN)
dp = Dispatcher(bot)


def auth(func):

    async def wrapper(message):
        if message.from_user.username in username_white_list:
            return await message.reply("Нет доступа", reply=False)
        return await func(message)

    return wrapper


@dp.message_handler(commands=['start', 'help'])
@auth
async def greeting_reply(message: types.Message):
    await message.reply('Привет! Я могу присылать прогноз погоды на завтра!\n\
Напиши /today для прогноза на сегодня и /tomorrow для прогноза на завтра.')


@dp.message_handler(commands=['today', 'tomorrow'])
@auth
async def forecast_answer(message: types.Message):
    if message.text == '/today':
        forecast_answer_text = get_forecast.get_forecast_text(0)
    elif message.text == '/tomorrow':
        forecast_answer_text = get_forecast.get_forecast_text(1)
    await message.answer(forecast_answer_text)


@dp.message_handler()
@auth
async def unknown_command_answer(message: types.Message):
    await message.reply('Напиши /today для прогноза на сегодня и /tomorrow для прогноза на завтра.')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
