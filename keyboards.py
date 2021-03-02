from  aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button_help = InlineKeyboardButton('Вызвать помощь', callback_data='help')
help_kb = InlineKeyboardMarkup().add(button_help)

create_button = KeyboardButton('Создать аккаунт')
account_button = InlineKeyboardButton('Инфо об аккаунте')
main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(create_button, account_button)
