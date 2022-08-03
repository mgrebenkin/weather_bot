from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text=r'/today'),
            KeyboardButton(text=r'/tomorrow')
        ],
        [
            KeyboardButton(text=r'/subscribe'),
            KeyboardButton(text=r'/unsubscribe')
        ]
    ], resize_keyboard=True
)

request_location_markup = ReplyKeyboardMarkup(
    keyboard=[[
        KeyboardButton(text='Поделиться местоположением', request_location=True)
    ]], one_time_keyboard=True, resize_keyboard=True
)