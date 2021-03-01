from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


button_help = InlineKeyboardButton('Вызвать помощь', callback_data='help')
help_kb = InlineKeyboardMarkup().add(button_help)

create_button = KeyboardButton('/create')
account_button = InlineKeyboardButton('/account')
main_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(create_button, account_button)
