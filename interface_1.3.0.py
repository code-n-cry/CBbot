import json
import os
import logging
import moneywagon
import requests
import aiogram
import asyncio
from aiogram import Dispatcher, Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ReplyKeyboardRemove, ParseMode
from aiogram.utils.markdown import bold
from aiogram.utils import executor
from constants import phrases, keyboards
from constants.exceptions import *
from smtplib import SMTPRecipientsRefused
from time import sleep
from emoji import emojize
from data import db_session
from data.user import User
from data.verification import IsVerifying
from data.waiting_for_money import IsPaying
from data.doing_diagramm import DoingDiagram
from modules.math_operations import add_session
from modules.crypto_operations import CryptoOperating
from modules.payment_operations import PaymentOperations
from modules.email_operations import EmailOperations
from constants.states import *

db_session.initialization()
with open('static/json/phrases.json', encoding='utf-8') as phrases_json:
    all_data = json.load(phrases_json)
    str_phrases = all_data['str_phrases']
    list_phrases = all_data['list_phrases']

with open('static/json/general_bot_info.json', encoding='utf-8') as tokens:
    all_data = json.load(tokens)
    qiwi_token = all_data['Tokens']['Qiwi']
    qiwi_phone = all_data['Tokens']['Qiwi_phone']
    token = all_data['Tokens']['Tg_Token']
    dogecoin_wallet = all_data['Wallets']['DOGE']

with open('static/json/crypto_fees.json', encoding='utf-8') as fees:
    all_data = json.load(fees)
    crypto_fees = all_data['Fees']

with open('static/json/general_bot_info.json', encoding='utf-8') as input_json:
    all_data = json.load(input_json)
    bot_email = all_data['Email']['email']
    bot_password = all_data['Email']['password']

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())
crypto_operations = CryptoOperating()
email_operations = EmailOperations(bot_email, bot_password)
crypto_to_their_operations = {
    'BTC': crypto_operations.generate_bitcoin_wallet,
    'LTC': crypto_operations.generate_litecoin_wallet,
    'DOGE': crypto_operations.generate_dogecoin_wallet
}
qiwi_links_generator = PaymentOperations(qiwi_token, qiwi_phone)
is_paying = False


# Функции для проверки статуса пользователя в системе"""
def is_user_logged(tg_user_id: int):
    session = db_session.create_session()
    check = session.query(User).get(tg_user_id)
    if check:
        return True
    return False


def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


def is_wallet_already_bound(crypto_abbreviation: str, tg_user_id: int) -> str:
    session = db_session.create_session()
    chosen_crypto = phrases.abbreviations_to_crypto[crypto_abbreviation]
    user = session.query(User).filter(User.id == tg_user_id).first()
    if eval(f'user.{chosen_crypto}_wallet'):
        return eval(f'user.{chosen_crypto}_wallet')
    return ''


async def delete_message(message: types.Message, sleep_time: int):
    await asyncio.sleep(sleep_time)
    await message.delete()


# Стартовая команда
@dp.message_handler(commands=['start'])
async def process_start_command(message: types.message):
    name = message.from_user.first_name
    await bot.send_message(message.from_user.id, phrases.start_phrase(name),
                           reply_markup=keyboards.help_kb)


# Команда "помощь" и кнопки для неё
@dp.callback_query_handler(lambda call: True)
async def process_callbacks(call):
    if call.data == 'help':
        reply_markup = keyboards.main_kb
        if not is_user_logged(call.from_user.id):
            reply_markup = keyboards.newbie_kb
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.from_user.id, '\n'.join(list_phrases['help_message']),
                               reply_markup=reply_markup)


@dp.message_handler(commands=['помощь', 'help'])
async def process_help_command(message: types.message):
    reply_markup = keyboards.main_kb
    await types.ChatActions.typing()
    if not is_user_logged(message.from_user.id):
        reply_markup = keyboards.newbie_kb
    await bot.send_message(message.from_user.id, '\n'.join(list_phrases['help_message']),
                           reply_markup=reply_markup)


# операции, связанные с аккаунтном
@dp.message_handler(commands=['account'])
async def account_operations(message):
    reply_kb = keyboards.not_logged_kb
    msg_text = str_phrases['not_logged']
    if is_user_logged(message.from_user.id):
        reply_kb = keyboards.logged_kb
        msg_text = str_phrases['is_logged']
    await bot.send_message(message.from_user.id, msg_text, reply_markup=reply_kb)


@dp.message_handler(commands=['инфо', 'info'])
async def process_account_command(message: types.message):
    db_sess = db_session.create_session()
    await types.ChatActions.typing()
    if is_user_logged(message.from_user.id):
        btc_wallet = [user.bitcoin_wallet for user in
                      db_sess.query(User).filter(User.id == message.from_user.id)][0]
        ltc_wallet = [user.litecoin_wallet for user in
                      db_sess.query(User).filter(User.id == message.from_user.id)][0]
        eth_wallet = [user.ethereum_wallet for user in
                      db_sess.query(User).filter(User.id == message.from_user.id)][0]
        doge_wallet = [user.dogecoin_wallet for user in
                       db_sess.query(User).filter(User.id == message.from_user.id)][0]
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id,
                               phrases.account_info(btc_wallet, ltc_wallet, doge_wallet, eth_wallet),
                               reply_markup=keyboards.main_kb)
    else:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, emojize(str_phrases['no_account']),
                               reply_markup=keyboards.newbie_kb)


@dp.message_handler(commands=['create', 'создать'])
async def process_create_command(message: types.message):
    await types.ChatActions.typing()
    if is_user_logged(message.from_user.id):
        await bot.send_message(message.from_user.id, str_phrases['already_registered'])
    else:
        await bot.send_message(message.from_user.id, '\n'.join(list_phrases['creating_msg']),
                               reply_markup=keyboards.email_kb)


@dp.message_handler(commands=['email', 'почта'])
async def start_email_command(message: types.Message):
    await types.ChatActions.typing()
    if not is_user_logged(message.from_user.id):
        await bot.send_message(message.from_user.id, str_phrases['send_me_email'],
                               reply_markup=ReplyKeyboardRemove())
        await GetEmail.waiting_for_email.set()
    else:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, str_phrases['already_registered'])


async def email_sent(message, state):
    try:
        mail = message.text
        session = db_session.create_session()
        is_email_in_db = [user for user in session.query(User).filter(User.email == mail)]
        if not is_email_in_db:
            code = email_operations.verify_email(mail, message.from_user.first_name)
            data = IsVerifying()
            data.id = message.from_user.id
            data.code = code
            session = db_session.create_session()
            session.add(data)
            session.commit()
            await state.update_data(email=mail)
            await types.ChatActions.typing()
            await bot.send_message(message.from_user.id, str_phrases['code_sent'],
                                   reply_markup=ReplyKeyboardRemove())
            await bot.send_message(message.from_user.id, str_phrases['send_code_next'])
            await GetEmail.next()
        else:
            await types.ChatActions.typing()
            await bot.send_message(message.from_user.id, str_phrases['this_mail_used'],
                                   reply_markup=ReplyKeyboardRemove())
            await state.finish()
    except EmailDoesNotExists:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['invalid_email'],
                               reply_markup=keyboards.newbie_kb)
        await state.finish()
    except SMTPRecipientsRefused:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['invalid_email'],
                               reply_markup=keyboards.newbie_kb)
        await state.finish()


async def code_sent(message, state):
    session = db_session.create_session()
    try:
        user_codes = [data.code for data in
                      session.query(IsVerifying).filter(IsVerifying.id == message.from_user.id)]
        if user_codes:
            email = await state.get_data()
            code = int(message.text)
            right_code = user_codes[-1]
            if code == right_code:
                new_user = User()
                new_user.id = message.from_user.id
                new_user.email = email['email']
                session.add(new_user)
                session.commit()
                logging.info(f'new user: {new_user.id}')
                await types.ChatActions.typing()
                await bot.send_message(message.from_user.id, '\n'.join(list_phrases['code_success']),
                                       reply_markup=keyboards.main_kb)
                session.query(IsVerifying).filter(
                    IsVerifying.id == message.from_user.id).delete()
                session.commit()
                await state.finish()
            else:
                await types.ChatActions.typing()
                await bot.send_message(message.from_user.id, str_phrases['invalid_email'],
                                       reply_markup=keyboards.newbie_kb)
                await state.finish()
        else:
            await types.ChatActions.typing()
            await bot.send_message(message.from_user.id, str_phrases['mail_not_specified'],
                                   reply_markup=keyboards.newbie_kb)
            await state.finish()
    except ValueError:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['invalid_code'],
                               reply_markup=keyboards.newbie_kb)
        await state.finish()


@dp.message_handler(commands=['bind'])
async def bind_command_start(message: types.Message):
    msg_text = "В следующем сообщении выберите нужную криптовалюту:"
    reply_kb = keyboards.cryptos_kb
    await types.ChatActions.typing(2)
    await bot.send_message(message.from_user.id, msg_text, reply_markup=reply_kb)
    await BindWallet.waiting_for_crypto.set()


async def waiting_for_crypto_for_bind(message: types.Message, state):
    chosen_crypto = message.text
    if chosen_crypto not in phrases.available_crypto:
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    crypto_abbreviation = phrases.cryptos_abbreviations[chosen_crypto]
    await types.ChatActions.typing(2)
    await state.update_data(chosen_crypto=crypto_abbreviation)
    if is_wallet_already_bound(crypto_abbreviation, message.from_user.id):
        await bot.send_message(message.from_user.id,
                               phrases.wallet_already_bound(crypto_abbreviation),
                               reply_markup=keyboards.yes_or_no_kb)
        await BindWallet.next()
        return
    await bot.send_message(message.from_user.id, str_phrases['send_wallet_variant'],
                           reply_markup=keyboards.variants_kb)
    await BindWallet.waiting_for_variant.set()


async def bind_again_or_no(message: types.Message, state):
    if message.text.lower() not in phrases.available_variants2:
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
    if message.text.lower() == 'да✔️':
        await bot.send_message(message.from_user.id, str_phrases['send_wallet_variant'],
                               reply_markup=keyboards.variants_kb)
        await BindWallet.next()
    if message.text.lower() == 'нет❌':
        await bot.send_message(message.from_user.id, 'Операция отменена',
                               reply_markup=keyboards.main_kb)
        await state.finish()


async def waiting_for_bind_variant(message: types.Message, state):
    if message.text not in phrases.available_variants:
        await bot.send_message(message.from_user.id,
                               'Пожалуйста, выбирайте из предложенных вариантов')
        return
    chosen_variant = message.text
    state_data = await state.get_data()
    if chosen_variant == phrases.available_variants[0]:
        # если пользователь хочет сгенерировать кошелёк себе
        abbreviation_to_function = {
            'BTC': crypto_operations.generate_bitcoin_wallet,
            'LTC': crypto_operations.generate_litecoin_wallet,
            'DOGE': crypto_operations.generate_dogecoin_wallet,
            'ETH': crypto_operations.generate_eth_wallet
        }
        address, private = abbreviation_to_function[state_data['chosen_crypto']]()
        await types.ChatActions.typing(2)
        msg = await bot.send_message(message.from_user.id,
                                     phrases.wallet_info(address, private,
                                                         state_data['chosen_crypto']),
                                     reply_markup=keyboards.main_kb,
                                     parse_mode=ParseMode.MARKDOWN)
        media = types.MediaGroup()
        try:
            media.attach_photo(
                f'https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl={address}',
                'QR-код вашего кошелька')
        except aiogram.utils.exceptions.InvalidHTTPUrlContent:
            media.attach_photo(
                f'https://chart.googleapis.com/chart?chs=250x250&cht=qr&chl={address}',
                'QR-код вашего кошелька')  # как показала практика, со второго раза работает
        await types.ChatActions.upload_photo(2)
        await msg.reply_media_group(media=media)
        session = db_session.create_session()
        current_user = session.query(User).filter(User.id == message.from_user.id).first()
        exec(
            f'current_user.{phrases.abbreviations_to_crypto[state_data["chosen_crypto"]]}_wallet="{address}"')
        session.merge(current_user)
        session.commit()
        await state.finish()
        # выше конструкция для занесения в базу данных адреса кошелька,
        # т.к. удобнее способа мы не нашли, данные добавляются через форматированную строку
    else:
        await bot.send_message(message.from_user.id,
                               f'Хорошо, теперь пришлите адрес {state_data["chosen_crypto"]}-кошелька:',
                               reply_markup=ReplyKeyboardRemove())
        await BindWallet.next()


async def wallet_for_bind_sent(message: types.Message, state):
    try:
        address = message.text
        state_data = await state.get_data()
        if crypto_operations.check_crypto_wallet(state_data['chosen_crypto'], address):
            await bot.send_message(message.from_user.id, str_phrases['wallet_ok'],
                                   reply_markup=keyboards.main_kb)
            session = db_session.create_session()
            current_user = session.query(User).filter(User.id == message.from_user.id).first()
            exec(
                f'current_user.{phrases.abbreviations_to_crypto[state_data["chosen_crypto"]]}_wallet="{address}"')
            session.add(current_user)
            session.commit()
            await state.finish()
    except InvalidAddress:
        await bot.send_message(message.from_user.id, str_phrases['invalid_wallet'],
                               reply_markup=keyboards.main_kb)
        await state.finish()


# операции с криптовалютами
@dp.message_handler(commands=['crypto'])
async def crypto_actions(message):
    if is_user_logged(message.from_user.id):
        await bot.send_message(message.from_user.id,
                               'Сейчас в нашей системе доступны такие операции(на клавиатуре):',
                               reply_markup=keyboards.available_crypto_operations)
        return
    await bot.send_message(message.from_user.id, str_phrases['u_need_account'])


@dp.message_handler(commands=['balance', 'баланс'])
async def process_balance_command(message: types.message):
    if is_user_logged(message.from_user.id):
        await types.ChatActions.typing(3)
        await bot.send_message(message.from_user.id, str_phrases['choose_currency'],
                               reply_markup=keyboards.cryptos_kb)
        await CheckBalance.waiting_for_crypto.set()
    else:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, str_phrases['u_need_account'],
                               reply_markup=keyboards.newbie_kb)


async def crypto_for_balance_chosen(message: types.Message, state: aiogram.dispatcher.filters.state):
    chosen_crypto = message.text
    if chosen_crypto not in phrases.available_crypto:
        await types.ChatActions.typing(3)
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    await state.update_data(chosen_crypto=chosen_crypto.lower())
    print(message.from_user.id)
    wallet = is_wallet_already_bound(phrases.cryptos_abbreviations[chosen_crypto],
                                     message.from_user.id)
    await state.update_data(chosen_crypto=phrases.cryptos_abbreviations[chosen_crypto])
    if wallet:
        await state.update_data(need_wallet=wallet)
        await bot.send_message(message.from_user.id, str_phrases['use_bounded?'],
                               reply_markup=keyboards.yes_or_no_kb)
        await CheckBalance.wallet_is_bound.set()
    else:
        await bot.send_message(message.from_user.id, str_phrases['send_wallet_next'],
                               reply_markup=ReplyKeyboardRemove())
        await CheckBalance.wallet_not_bound.set()


async def use_bounded_wallet(message: types.Message, state: aiogram.dispatcher.filters.state):
    if message.text.lower() not in phrases.available_variants2:
        await bot.send_message(message.from_user.id,
                               'Пожалуйста, выберите из вариантов на клавиатуре',
                               reply_markup=keyboards.yes_or_no_kb)
        return
    if message.text == 'Нет❌':
        await bot.send_message(message.from_user.id, 'Хорошо, тогда отправьте нужный Вам адрес:',
                               reply_markup=ReplyKeyboardRemove())
        await CheckBalance.wallet_not_bound.set()
    if message.text == 'Да✔️':
        data = await state.get_data()
        wallet = data['need_wallet']
        chosen_crypto = data['chosen_crypto']
        balance = crypto_operations.check_crypto_wallet(chosen_crypto, wallet)
        msg_text = f'Баланс этого {chosen_crypto}-кошелька: {balance} {chosen_crypto}'
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, msg_text, reply_markup=keyboards.main_kb)
        await state.finish()


async def wallet_not_bound(message: types.Message, state):
    wallet = message.text
    state_data = await state.get_data()
    chosen_crypto = state_data['chosen_crypto']
    try:
        balance = crypto_operations.check_crypto_wallet(chosen_crypto, wallet)
        msg_text = f'Баланс этого {chosen_crypto}-кошелька: {balance} {chosen_crypto}'
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, msg_text, reply_markup=keyboards.main_kb)
        await state.finish()
    except InvalidAddress:
        msg_text = ['Кошелёк не прошёл проверку на правильность', 'Вероятно, вы ошиблись']
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, '\n'.join(msg_text),
                               reply_markup=keyboards.main_kb)
        await state.finish()


@dp.message_handler(commands=['price_operations'])
async def price_operations(message: types.Message):
    reply_kb = keyboards.price_kb
    await bot.send_message(message.from_user.id, 'Выберите нужный вам вариант(на клавиатуре ниже):',
                           reply_markup=reply_kb)


@dp.message_handler(commands=['price', 'курс'])
async def start_price_command(message):
    await types.ChatActions.typing()
    keyboard = keyboards.cryptos_kb
    await bot.send_message(message.from_user.id, 'Выберите валюту из предложенных',
                           reply_markup=keyboard)
    await GetPrice.waiting_for_crypto.set()


async def crypto_chosen(message, state):
    await types.ChatActions.typing()
    if message.text.capitalize() not in phrases.available_crypto:
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    await state.update_data(chosen_crypto=message.text.capitalize())
    await GetPrice.next()
    await bot.send_message(message.from_user.id, 'К какой валюте привести?',
                           reply_markup=keyboards.fiat_kb)


async def fiat_chosen(message, state):
    if message.text.lower() not in phrases.available_fiat:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_crypto = await state.get_data()
    chosen_fiat = message.text.lower()
    chosen_crypto_code = phrases.cryptos_abbreviations[chosen_crypto['chosen_crypto']]
    chosen_fiat_code = phrases.fiats_abbreviations[chosen_fiat]
    price = round(moneywagon.get_current_price(chosen_crypto_code, chosen_fiat_code), 2)
    fiat_to_genitive = phrases.fiats_genitive[chosen_fiat]
    reply_markup = keyboards.main_kb
    session = db_session.create_session()
    is_user_in_db = [user for user in session.query(User).filter(User.id == message.from_user.id)]
    if not is_user_in_db:
        reply_markup = keyboards.newbie_kb
    await types.ChatActions.typing()
    await bot.send_message(message.from_user.id,
                           phrases.price_info(chosen_crypto['chosen_crypto'], fiat_to_genitive,
                                              price, chosen_fiat_code),
                           reply_markup=reply_markup)
    await state.finish()


@dp.message_handler(commands=['graph', 'график'])
async def start_graph_command(message):
    keyboard = keyboards.cryptos_kb
    await BuildGraph.waiting_for_crypto.set()
    await types.ChatActions.typing()
    await bot.send_message(message.from_user.id, "Выберите криптовалюту из предложенных:",
                           reply_markup=keyboard)


async def crypto_for_graph_chosen(message):
    if message.text.capitalize() not in phrases.available_crypto:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_crypto_code = phrases.cryptos_abbreviations[message.text.capitalize()]
    await types.ChatActions.typing()
    await bot.send_message(message.from_user.id, 'К какой валюте привести?',
                           reply_markup=keyboards.fiat_kb)
    session = db_session.create_session()
    diagram = DoingDiagram(id=message.from_user.id, chosen_crypto=chosen_crypto_code)
    session.add(diagram)
    session.commit()
    await BuildGraph.next()


async def fiat_for_graph_chosen(message):
    if message.text.lower() not in phrases.available_fiat:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_fiat_code = phrases.fiats_abbreviations[message.text.lower()]
    await types.ChatActions.typing()
    await bot.send_message(message.from_user.id,
                           'Отлично! Теперь выберите период, за который отобразить цену',
                           reply_markup=keyboards.periods_kb)
    session = db_session.create_session()
    diagram = session.query(DoingDiagram).filter(DoingDiagram.id == message.from_user.id).first()
    diagram.chosen_fiat = chosen_fiat_code
    session.commit()
    await BuildGraph.next()


async def period_for_graph_chosen(message, state):
    session = db_session.create_session()
    if message.text.capitalize() not in phrases.available_periods:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_period = message.text.capitalize()
    current_user_data = session.query(DoingDiagram).filter(
        DoingDiagram.id == message.from_user.id).first()
    chosen_crypto = current_user_data.chosen_crypto
    chosen_fiat = current_user_data.chosen_fiat
    filename = 'static/img/'
    all_pngs = []
    for file_name in os.listdir(filename):
        if file_name.endswith('.png'):
            all_pngs.append(file_name.split('.png')[0])
    if all_pngs:
        last_num = int(all_pngs[-1][-1])
        filename += f'plot{last_num + 1}'
    else:
        filename = f'plot{0}'
    add_session(chosen_period, chosen_crypto, chosen_fiat, filename)
    await types.ChatActions.upload_photo(2)
    media = types.MediaGroup()
    media.attach_photo(types.InputFile(filename + '.png'), caption='Ваша диаграмма!')
    await message.reply_media_group(media=media)
    reply_markup = keyboards.main_kb
    session.delete(current_user_data)
    session.commit()
    is_user_in_db = [user for user in
                     session.query(User).filter(User.id == message.from_user.id)]
    if not is_user_in_db:
        reply_markup = keyboards.newbie_kb
    await types.ChatActions.typing(1)
    await bot.send_message(message.from_user.id, 'Возращаем вас к основному интерфейсу...',
                           reply_markup=reply_markup)
    await state.finish()


@dp.message_handler(commands=['buy', 'купить'])
async def start_buying_command(message: types.message):
    if is_user_logged(message.from_user.id):
        await types.ChatActions.typing(2)
        await BuyingState.waiting_for_crypto.set()
        await bot.send_message(message.from_user.id, '\n'.join(list_phrases['start_buying']),
                               reply_markup=keyboards.tx_kb)
    else:
        await bot.send_message(message.from_user.id, str_phrases['u_need_account'])


async def crypto_for_buy_chosen(message: types.message, state):
    chosen_crypto = message.text
    if chosen_crypto not in phrases.available_crypto:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    await types.ChatActions.typing()
    await state.update_data(chosen_crypto=chosen_crypto)
    await bot.send_message(message.from_user.id, 'Теперь напишите количество, необходимое вам:',
                           reply_markup=ReplyKeyboardRemove())
    await BuyingState.next()


async def generating_code(message: types.message, state):
    try:
        chosen_amount = float(message.text.replace(',', '.'))
        if chosen_amount <= 0:
            raise AmountError
        session = db_session.create_session()
        state_data = await state.get_data()
        chosen_crypto = state_data['chosen_crypto']
        await state.update_data(chosen_amount=chosen_amount)
        our_amount = crypto_operations.get_balance(phrases.cryptos_abbreviations[chosen_crypto])
        if our_amount <= chosen_amount:
            await bot.send_message(message.from_user.id, str_phrases['so_poor'],
                                   reply_markup=keyboards.main_kb)
            await state.finish()
            return
        rub_price = moneywagon.get_current_price(phrases.cryptos_abbreviations[chosen_crypto], 'RUB')
        rub_and_cop = round(round(rub_price, 2) * (chosen_amount + crypto_fees[chosen_crypto]), 2)
        if not rub_and_cop.is_integer():
            link = qiwi_links_generator.create_bill(int(str(rub_and_cop).split('.')[0]),
                                                    int(str(rub_and_cop).split('.')[1]))
        else:
            link = qiwi_links_generator.create_bill(rub_and_cop, 0)
        headers = {
            'Authorization': 'Bearer 77397c6ca2362f76abb2bdff47d1b6bb44c0fdff',
            "Content-Type": "application/json"
        }
        json_params = {
            'long_url': link
        }
        response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers,
                                 json=json_params).json()
        await types.ChatActions.typing(2)
        code = qiwi_links_generator.generate_payment_code()
        await state.update_data(tx_code=code)
        new_code = IsPaying(id=message.from_user.id, code=code,
                            crypto_currency_name=phrases.cryptos_abbreviations[chosen_crypto])
        current_user = load_user(message.from_user.id)
        current_user.payment_codes.append(new_code)
        session.merge(current_user)
        session.commit()
        for_message = [f'Ваш код для оплаты: {code}',
                       bold(
                           'ОБЯЗАТЕЛЬНО УКАЖИТЕ ЕГО В КОММЕНТАРИЯХ К ПЛАТЕЖУ, ИНАЧЕ ПОТЕРЯЕТЕ ДЕНЬГИ')]
        await bot.send_message(message.from_user.id, '\n'.join(for_message),
                               parse_mode=ParseMode.MARKDOWN)
        link = response['link']
        await types.ChatActions.typing(2)
        msg = phrases.all_okay(chosen_crypto, link)
        await bot.send_message(message.from_user.id, msg, reply_markup=keyboards.payment_kb)
        await BuyingState.next()
    except ValueError:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, str_phrases['just_number'])
        return
    except AmountError:
        await types.ChatActions.typing(3)
        await bot.send_message(message.from_user.id, str_phrases['invalid_amount'])
        return


async def send_me_wallet(message: types.message, state):
    reply_markup = keyboards.main_kb
    session = db_session.create_session()
    state_data = await state.get_data()
    need_data = session.query(IsPaying).filter(IsPaying.id == message.from_user.id).all()
    need_code = need_data[-1].code
    sleep(2.5)
    payment_history = qiwi_links_generator.get_all_history()
    for data in payment_history['data']:
        if data['comment'] == need_code:
            break
    else:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id,
                               'К сожалению, ваш платёж не обнаружен и отменён.',
                               reply_markup=reply_markup)
        await state.finish()
        return
    await types.ChatActions.typing(4)
    need_crypto = need_data[-1].crypto_currency_name
    await state.update_data(chosen_crypto=need_crypto)
    wallet = is_wallet_already_bound(need_crypto, message.from_user.id)
    phrase = ['Отлично, платёж прошёл успешно!',
              f'Отправьте номер вашего {need_crypto}-кошелька:']
    phrase2 = ['Отлично, платёж прошёл успешно!',
               f'Транзакция будет отправлена на привязанный {need_crypto} кошелёк!']
    if wallet:
        try:
            tx_code = state_data['tx_code']
            chosen_amount = state_data['chosen_amount']
            user = session.query(User).filter(User.id == message.from_user.id).first()
            user_email = user.email
            tx_hash = crypto_operations.send_transaction(need_crypto, wallet, int(chosen_amount))
            email_operations.send_buy_info(user_email, tx_code, need_crypto, chosen_amount, tx_hash)
            await bot.send_message(message.from_user.id, '\n'.join(phrase2),
                                   reply_markup=keyboards.main_kb)
            for data in need_data:
                session.delete(data)
            session.commit()
            await state.finish()
        except Exception:
            await bot.send_message(message.from_user.id, str_phrases['error_occurred'],
                                   reply_markup=keyboards.main_kb)
            await state.finish()
    else:
        await bot.send_message(message.from_user.id, '\n'.join(phrase),
                               reply_markup=ReplyKeyboardRemove())
        for data in need_data:
            session.delete(data)
        session.commit()
        await BuyingState.next()


async def finishing(message: types.Message, state):
    session = db_session.create_session()
    user = session.query(User).filter(User.id == message.from_user.id).first()
    user_email = user.email
    data = await state.get_data()
    wallet = message.text
    chosen_crypto = data['chosen_crypto']
    chosen_amount = data['chosen_amount']
    tx_code = data['tx_code']
    try:
        crypto_operations.check_crypto_wallet(chosen_crypto, wallet)
        tx_hash = crypto_operations.send_transaction(chosen_crypto, wallet,
                                                     int(data['chosen_amount']))
        await bot.send_message(message.from_user.id, str_phrases['tx_sent'])
        email_operations.send_buy_info(user_email, tx_code, chosen_crypto, chosen_amount, tx_hash)
        await state.finish()
    except InvalidAddress:
        await bot.send_message(message.from_user.id, str_phrases['invalid_wallet'],
                               reply_markup=keyboards.main_kb)
        return


@dp.message_handler(commands=['transaction'])
async def process_transaction_command(message: types.Message):
    user_id = message.from_user.id
    if is_user_logged(user_id):
        await bot.send_message(user_id, str_phrases['choose_currency_for_tx'],
                               reply_markup=keyboards.tx_kb)
        await SendTransaction.waiting_for_crypto.set()
    else:
        await bot.send_message(user_id, str_phrases['u_need_account'],
                               reply_markup=keyboards.newbie_kb)


async def crypto_for_transaction_chosen(message: types.Message, state):
    chosen_crypto = message.text
    user_id = message.from_user.id
    if chosen_crypto not in phrases.available_crypto[:-1]:
        await bot.send_message(user_id, str_phrases['choose_available'])
        return
    await state.update_data(chosen_crypto=phrases.cryptos_abbreviations[chosen_crypto])
    await bot.send_message(user_id, str_phrases['send_secret_key_next'],
                           reply_markup=ReplyKeyboardRemove())
    await SendTransaction.waiting_for_secret_key.set()


async def private_key_sent(message: types.Message, state):
    user_id = message.from_user.id
    private_key = message.text
    await state.update_data(private_key=private_key)
    await bot.send_message(user_id, str_phrases['send_amount'], reply_markup=ReplyKeyboardRemove())
    await SendTransaction.waiting_for_amount.set()


async def amount_sent(message: types.Message, state):
    user_id = message.from_user.id
    try:
        amount = float(message.text)
        if amount <= 0:
            raise AmountError
        await state.update_data(chosen_amount=amount)
        await bot.send_message(user_id, str_phrases['send_wallet_for_tx'],
                               reply_markup=ReplyKeyboardRemove())
        await SendTransaction.waiting_for_wallet_to_send.set()
    except ValueError:
        await bot.send_message(user_id, str_phrases['just_number'])
        return
    except AmountError:
        await bot.send_message(user_id, str_phrases['invalid_amount'])
        return


async def wallet_sent(message: types.Message, state):
    user_id = message.from_user.id
    try:
        state_data = await state.get_data()
        chosen_crypto = state_data['chosen_crypto']
        chosen_amount = state_data['chosen_amount']
        private_key = state_data['private_key']
        wallet = message.text
        crypto_operations.check_crypto_wallet(chosen_crypto, wallet)
        tx_hash = crypto_operations.send_transaction(chosen_crypto, wallet, chosen_amount,
                                                     private_key=private_key)
        msg_text = [f'Транзакция на кошелёк {wallet} отправлена!',
                    f'ID транзакции: {tx_hash}']
        await bot.send_message(message.from_user.id, '\n'.join(msg_text),
                               reply_markup=keyboards.main_kb)
    except InvalidAddress:
        await bot.send_message(user_id, str_phrases['invalid_wallet'],
                               reply_markup=keyboards.main_kb)
        await state.finish()
    except AssertionError:
        await bot.send_message(user_id, str_phrases['invalid_private_key'],
                               reply_markup=keyboards.main_kb)
    except Exception:
        await bot.send_message(user_id, str_phrases['bad_tx'], reply_markup=keyboards.main_kb)


@dp.message_handler(commands=['/status'])
async def start_status_command(message: types.Message):
    user_id = message.from_user.id
    if not load_user(user_id):
        await bot.send_message(user_id, str_phrases['u_need_account'],
                               reply_markup=keyboards.newbie_kb)
        return
    await bot.send_message(user_id, str_phrases['choose_crypto_network'],
                           reply_markup=keyboards.cryptos_kb)
    await SendTransaction.waiting_for_crypto.set()


async def crypto_for_status_chosen(message: types.Message, state):
    user_id = message.from_user.id
    if message.text not in phrases.available_crypto:
        await bot.send_message(user_id, str_phrases['pls_choose_available'])
        return
    await state.update_data(chosen_crypto=message.text)
    await bot.send_message(user_id, str_phrases['input_tx_hash'], reply_markup=ReplyKeyboardRemove())
    await CheckStatus.waiting_for_tx_hash.set()


async def tx_hash_sent(message: types.Message, state):
    user_id = message.from_user.id
    state_data = await state.get_data()
    tx_hash = message.text
    try:
        chosen_crypto = phrases.cryptos_abbreviations[state_data['chosen_crypto']]
        tx_status = crypto_operations.check_chain_transaction(chosen_crypto, tx_hash)
        msg_text = str_phrases['unconfirmed_tx']
        if tx_status == 2:
            msg_text = str_phrases['processing_tx']
        if tx_status == 3:
            msg_text = str_phrases['confirmed_tx']
        await bot.send_message(user_id, msg_text, reply_markup=keyboards.main_kb)
        await state.finish()
    except BadTransaction:
        await bot.send_message(user_id, str_phrases['invalid_tx'], reply_markup=keyboards.main_kb)
        await state.finish()


# привязка текста к операциям
@dp.message_handler()
async def process_text(message):
    """Делаем так, чтобы комманды были доступны с помощью клавиатуры и обычных фраз, а не только
    команд типа /команда"""
    if message.text.lower() == 'помощь':
        await process_help_command(message)
    if message.text.lower() == 'создать аккаунт👦':
        await process_create_command(message)
    if message.text.lower() == 'инфо об аккаунте🗄️':
        await process_account_command(message)
    if message.text.lower() == 'привязать криптовалютный кошелёк👛':
        await bind_command_start(message)
    if message.text.lower() == 'узнать о стоимости криптовалют💱':
        await price_operations(message)
    if message.text.lower() == 'курсы криптовалют сегодня🧮':
        await start_price_command(message)
    if message.text.lower() == 'график стоимости за период📈':
        await start_graph_command(message)
    if message.text.lower() == 'привязать почту📩':
        await start_email_command(message)
    if message.text.lower() == 'график стоимости📈':
        await start_graph_command(message)
    if message.text.lower() == 'купить криптовалюту💳':
        await start_buying_command(message)
    if message.text.lower() == 'операции с аккаунтом🧾':
        await account_operations(message)
    if message.text.lower() == 'операции с криптовалютами💲':
        await crypto_actions(message)
    if message.text.lower() == 'проверить баланс кошелька💰':
        await process_balance_command(message)
    if message.text.lower() == 'отправить крипто-транзакцию💸':
        await process_transaction_command(message)


# связываем функции и классы из файла states.py для ведения диалогов
def register_handlers_price(dispatcher):
    dispatcher.register_message_handler(start_price_command, commands="price", state='*')
    dispatcher.register_message_handler(crypto_chosen, state=GetPrice.waiting_for_crypto)
    dispatcher.register_message_handler(fiat_chosen, state=GetPrice.waiting_for_fiat)


def register_mail_handlers(dispatcher):
    dispatcher.register_message_handler(start_email_command, commands="email", state='*')
    dispatcher.register_message_handler(email_sent, state=GetEmail.waiting_for_email)
    dispatcher.register_message_handler(code_sent, state=GetEmail.waiting_for_code)


def register_graph_handlers(dispatcher):
    dispatcher.register_message_handler(start_graph_command, commands="graph", state='*')
    dispatcher.register_message_handler(crypto_for_graph_chosen, state=BuildGraph.waiting_for_crypto)
    dispatcher.register_message_handler(fiat_for_graph_chosen, state=BuildGraph.waiting_for_fiat)
    dispatcher.register_message_handler(period_for_graph_chosen, state=BuildGraph.waiting_for_period)


def register_buy_handlers(dispatcher):
    dispatcher.register_message_handler(start_buying_command, commands="buy", state='*')
    dispatcher.register_message_handler(crypto_for_buy_chosen, state=BuyingState.waiting_for_crypto)
    dispatcher.register_message_handler(generating_code, state=BuyingState.waiting_for_amount)
    dispatcher.register_message_handler(send_me_wallet, state=BuyingState.waiting_for_wallet)
    dispatcher.register_message_handler(finishing, state=BuyingState.wallet_sent)


def register_bind_handlers(dispatcher):
    dispatcher.register_message_handler(bind_command_start, commands="bind", state='*')
    dispatcher.register_message_handler(waiting_for_crypto_for_bind,
                                        state=BindWallet.waiting_for_crypto)
    dispatcher.register_message_handler(bind_again_or_no, state=BindWallet.bind_again_or_no)
    dispatcher.register_message_handler(waiting_for_bind_variant,
                                        state=BindWallet.waiting_for_variant)
    dispatcher.register_message_handler(wallet_for_bind_sent, state=BindWallet.waiting_for_wallet)


def register_balance_handlers(dispatcher):
    dispatcher.register_message_handler(process_balance_command, commands="balance", state='*')
    dispatcher.register_message_handler(crypto_for_balance_chosen,
                                        state=CheckBalance.waiting_for_crypto)
    dispatcher.register_message_handler(wallet_not_bound, state=CheckBalance.wallet_not_bound)
    dispatcher.register_message_handler(use_bounded_wallet, state=CheckBalance.wallet_is_bound)


def register_transaction_handlers(dispatcher):
    dispatcher.register_message_handler(process_transaction_command, commands="tx", state='*')
    dispatcher.register_message_handler(crypto_for_transaction_chosen,
                                        state=SendTransaction.waiting_for_crypto)
    dispatcher.register_message_handler(private_key_sent,
                                        state=SendTransaction.waiting_for_secret_key)
    dispatcher.register_message_handler(amount_sent, state=SendTransaction.waiting_for_amount)
    dispatcher.register_message_handler(wallet_sent,
                                        state=SendTransaction.waiting_for_wallet_to_send)


def register_status_handlers(dispatcher):
    dispatcher.register_message_handler(start_status_command, commands='status', state='*')
    dispatcher.register_message_handler(crypto_for_status_chosen,
                                        state=CheckStatus.waiting_for_crypto)
    dispatcher.register_message_handler(tx_hash_sent, state=CheckStatus.waiting_for_tx_hash)


if __name__ == '__main__':
    register_handlers_price(dp)
    register_mail_handlers(dp)
    register_graph_handlers(dp)
    register_buy_handlers(dp)
    register_bind_handlers(dp)
    register_balance_handlers(dp)
    register_transaction_handlers(dp)
    register_status_handlers(dp)
    executor.start_polling(dp)
