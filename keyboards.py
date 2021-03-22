from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from phrases import available_crypto, fiats_for_buttons, available_periods


button_help = InlineKeyboardButton('Вызвать помощь', callback_data='help')
help_kb = InlineKeyboardMarkup().add(button_help)

create_button = KeyboardButton('Создать аккаунт')
account_button = KeyboardButton('Инфо об аккаунте')
price_button = KeyboardButton('Курсы валют💱')
graph_button = KeyboardButton('График стоимости📈')
buy_button = KeyboardButton('Купить криптовалюту💸')
newbie_kb = ReplyKeyboardMarkup().row(create_button, account_button)
newbie_kb.row(price_button)
newbie_kb.row(graph_button)

main_kb = ReplyKeyboardMarkup().row(account_button)
main_kb.row(price_button)
main_kb.row(graph_button)
main_kb.row(buy_button)

cryptos_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for currency in available_crypto:
    button = KeyboardButton(currency)
    cryptos_kb.add(button)

fiat_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for currency in fiats_for_buttons:
    button = KeyboardButton(currency)
    fiat_kb.add(button)

periods_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for period in available_periods:
    button = KeyboardButton(period)
    periods_kb.row(button)

email_btn = KeyboardButton('Привязать почту📩')
email_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(email_btn)
