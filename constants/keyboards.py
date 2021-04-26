from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton
from constants.phrases import available_crypto, fiats_for_buttons, available_periods

"""Account operations"""
account_operations = KeyboardButton('Операции с аккаунтом🧾')
create_button = KeyboardButton('Создать аккаунт👦')
info_button = KeyboardButton('Инфо об аккаунте🗄️')
news_button = KeyboardButton('Рассылка новостей📰')
bind_wallet = KeyboardButton('Привязать криптовалютный кошелёк👛')
want_generate = KeyboardButton('Хочу сгенерировать себе кошелёк🖨️')
want_bind_own = KeyboardButton('Хочу привязать собственный📝')
variants_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(want_generate).add(want_bind_own)
not_logged_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(create_button)
logged_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(info_button).row(bind_wallet).\
    row(news_button)
email_btn = KeyboardButton('Привязать почту📩')
email_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(email_btn)
"""Help command inline"""
button_help = InlineKeyboardButton('Вызвать помощь', callback_data='help')
help_kb = InlineKeyboardMarkup().add(button_help)
"""Payment operations"""
crypto_operations = KeyboardButton('Операции с криптовалютами💲')
buy_button = KeyboardButton('Купить криптовалюту💳')
balance_button = KeyboardButton('Проверить баланс кошелька💰')
tx_button = KeyboardButton('Отправить крипто-транзакцию💸')
status_button = KeyboardButton('Проверить статус транзакции🔖')
payment_button = KeyboardButton('Оплачено✔️')
available_crypto_operations = ReplyKeyboardMarkup(resize_keyboard=True).row(buy_button).row(
    tx_button, balance_button).row(status_button)
payment_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(payment_button)
"""Price info operations"""
price_operations = KeyboardButton('Узнать о стоимости криптовалют💱')
price_button = KeyboardButton('Курсы криптовалют сегодня🧮')
graph_button = KeyboardButton('График стоимости за период📈')
price_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(price_button).add(graph_button)
"""Main and newbie keyboards"""
newbie_kb = ReplyKeyboardMarkup(resize_keyboard=True).row(account_operations)
newbie_kb.row(price_operations)
main_kb = newbie_kb
main_kb.row(crypto_operations)
"""Keyboards with choose"""
cryptos_kb = ReplyKeyboardMarkup(resize_keyboard=True)  # клавиатура для выбора криптовалюты
tx_kb = ReplyKeyboardMarkup(resize_keyboard=True)
for currency in available_crypto:
    button = KeyboardButton(currency)
    cryptos_kb.add(button)
fiat_kb = ReplyKeyboardMarkup(
    resize_keyboard=True)  # клавиатура для выбора фиатной валюты(рубли и т.д.)
for currency in fiats_for_buttons:
    button = KeyboardButton(currency)
    fiat_kb.add(button)
periods_kb = ReplyKeyboardMarkup(resize_keyboard=True)  # клавиатура для выбора периода для графика
for period in available_periods:
    button = KeyboardButton(period)
    periods_kb.row(button)
for currency in available_crypto[:-1]:
    button = KeyboardButton(currency)
    tx_kb.row(button)
"""Yes or no keyboard"""
yes_button = KeyboardButton('Да✔️')
no_button = KeyboardButton('Нет❌')
yes_or_no_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(yes_button).add(no_button)
