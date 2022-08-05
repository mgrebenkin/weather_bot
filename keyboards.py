from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Прогноз на сегодня'),
            KeyboardButton(text='Прогноз на завтра')
        ],
        [
            KeyboardButton(text='Подписаться'),
            KeyboardButton(text='Отписаться')
        ],
        [
            KeyboardButton(text='Обновить местоположение', request_location=True)
        ]
    ], resize_keyboard=True
)

request_location_markup = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text='Поделиться местоположением', request_location=True)
    ]], one_time_keyboard=True, resize_keyboard=True
)