from math_operations import MathOperations
from modules.payment_operations import PaymentOperations
from states import GetPrice, GetEmail, BuildGraph, BuyingState
from aiogram import Dispatcher, Bot, types, executor
from aiogram.types import ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from checking_email import EmailDoesNotExists, verify_email
from checking_phone import checking_phone, WrongPhoneLength, PhoneNotRussian, SomeTextInThePhone
from smtplib import SMTPRecipientsRefused
from data import db_session
from data.verification import IsVerifying
from data.user import User
import keyboards
import os
import moneywagon
import requests
import json
import phrases

print('DB initialization.....')
db_session.initialization('db/all_data.sqlite')
with open('static/json/phrases.json', encoding='utf-8') as phrases_json:
    all_data = json.load(phrases_json)
    str_phrases = all_data['str_phrases']
    list_phrases = all_data['list_phrases']
with open('static/json/general_wallets.json', encoding='utf-8') as tokens:
    all_data = json.load(tokens)
    qiwi_token = all_data['Tokens']['Qiwi']
    token = all_data['Tokens']['Tg_Token']
    dogecoin_wallet = all_data['Wallets']['DOGE']
with open('static/json/crypto_fees.json', encoding='utf-8') as fees:
    all_data = json.load(fees)
    crypto_fees = all_data['Fees']
print('Bot starting...')
bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
plot_builder = MathOperations('', '', '', '')
qiwi_links_generator = PaymentOperations(qiwi_token, '79254461928')


@dp.message_handler(commands=['start'])
async def process_start_command(message):
    name = message.from_user.first_name
    await bot.send_message(message.from_user.id, phrases.start_phrase(name),
                           reply_markup=keyboards.help_kb)


@dp.callback_query_handler(lambda call: True)
async def process_callback_help_button(call):
    if call.data == 'help':
        reply_markup = keyboards.main_kb
        session = db_session.create_session()
        is_user_in_db = [user for user in
                         session.query(User).filter(User.id == call.from_user.id)]
        if not is_user_in_db:
            reply_markup = keyboards.newbie_kb
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.from_user.id, '\n'.join(list_phrases['help_message']),
                               reply_markup=reply_markup)


@dp.message_handler(commands=['помощь', 'help'])
async def process_help_command(message):
    reply_markup = keyboards.main_kb
    session = db_session.create_session()
    is_user_in_db = [user for user in session.query(User).filter(User.id == message.from_user.id)]
    await types.ChatActions.typing()
    if not is_user_in_db:
        reply_markup = keyboards.newbie_kb
    await bot.send_message(message.from_user.id, '\n'.join(list_phrases['help_message']),
                           reply_markup=reply_markup)


@dp.message_handler(commands=['create', 'создать'])
async def process_create_command(message):
    db_sess = db_session.create_session()
    is_user_in_db = [user for user in db_sess.query(User).filter(User.id == message.from_user.id)]
    await types.ChatActions.typing()
    if is_user_in_db:
        await bot.send_message(message.from_user.id, str_phrases['already_registered'])
    else:
        await bot.send_message(message.from_user.id, '\n'.join(list_phrases['creating_msg']),
                               reply_markup=keyboards.email_kb)


@dp.message_handler(commands=['account', 'инфо', 'info'])
async def process_account_command(message):
    db_sess = db_session.create_session()
    is_user_in_db = [user for user in db_sess.query(User).filter(User.id == message.from_user.id)]
    await types.ChatActions.typing()
    if is_user_in_db:
        btc_wallet = [user.bitcoin_wallet for user in
                      db_sess.query(User).filter(User.id == message.from_user.id)][0]
        ltc_wallet = [user.litecoin_wallet for user in
                      db_sess.query(User).filter(User.id == message.from_user.id)][0]
        eth_wallet = [user.ethereum_wallet for user in
                      db_sess.query(User).filter(User.id == message.from_user.id)][0]
        doge_wallet = [user.dogecoin_wallet for user in
                       db_sess.query(User).filter(User.id == message.from_user.id)][0]
        await bot.send_message(message.from_user.id,
                               phrases.account_info(btc_wallet, ltc_wallet, doge_wallet, eth_wallet))
    else:
        await bot.send_message(message.from_user.id, str_phrases['no_account'])


@dp.message_handler(commands=['email', 'почта'])
async def start_email_command(message):
    db_sess = db_session.create_session()
    is_user_in_db = [user for user in db_sess.query(User).filter(User.id == message.from_user.id)]
    await types.ChatActions.typing()
    if not is_user_in_db:
        await bot.send_message(message.from_user.id, str_phrases['send_me_email'])
        await GetEmail.waiting_for_email.set()
        return
    await bot.send_message(message.from_user.id, str_phrases['already_registered'])


async def email_sent(message, state):
    try:
        mail = message.text
        session = db_session.create_session()
        is_email_in_db = [user for user in session.query(User).filter(User.email == mail)]
        if not is_email_in_db:
            code = verify_email(mail, message.from_user.first_name)
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
            await bot.send_message(message.from_user.id, str_phrases['send_code_next'], )
            await GetEmail.next()
        else:
            await types.ChatActions.typing()
            await bot.send_message(message.from_user.id, str_phrases['this_mail_used'])
    except EmailDoesNotExists:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['invalid_email'],
                               reply_markup=keyboards.newbie_kb)
        state.finish()
    except SMTPRecipientsRefused:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['invalid_email'],
                               reply_markup=keyboards.newbie_kb)
        state.finish()


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
                state.finish()
        else:
            await types.ChatActions.typing()
            await bot.send_message(message.from_user.id, str_phrases['mail_not_specified'],
                                   reply_markup=keyboards.newbie_kb)
            state.finish()
    except ValueError:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['invalid_email'],
                               reply_markup=keyboards.newbie_kb)
        state.finish()


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
    await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'],
                           reply_markup=keyboard)


async def crypto_for_graph_chosen(message, state):
    if message.text.capitalize() not in phrases.available_crypto:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_crypto_code = phrases.cryptos_abbreviations[message.text.capitalize()]
    await types.ChatActions.typing()
    await bot.send_message(message.from_user.id, 'К какой валюте привести?',
                           reply_markup=keyboards.fiat_kb)
    await state.update_data(chosen_crypto=chosen_crypto_code)
    await BuildGraph.next()


async def fiat_for_graph_chosen(message, state):
    if message.text.lower() not in phrases.available_fiat:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_fiat_code = phrases.fiats_abbreviations[message.text.lower()]
    await types.ChatActions.typing()
    await bot.send_message(message.from_user.id,
                           'Отлично! Теперь выберите период, за который отобразить цену',
                           reply_markup=keyboards.periods_kb)
    await state.update_data(chosen_fiat=chosen_fiat_code)
    await BuildGraph.next()


async def period_for_graph_chosen(message, state):
    session = db_session.create_session()
    if message.text.capitalize() not in phrases.available_periods:
        await types.ChatActions.typing()
        await bot.send_message(message.from_user.id, str_phrases['pls_choose_available'])
        return
    chosen_period = message.text.capitalize()
    crypto_and_fiat = await state.get_data()
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
    plot_builder.set_new_data(chosen_period, crypto_and_fiat['chosen_crypto'],
                              crypto_and_fiat['chosen_fiat'], filename)
    plot_builder.main()
    await types.ChatActions.upload_photo()
    media = types.MediaGroup()
    media.attach_photo(types.InputFile(filename + '.png'))
    await message.reply_media_group(media=media)
    reply_markup = keyboards.main_kb
    is_user_in_db = [user for user in
                     session.query(User).filter(User.id == message.from_user.id)]
    if not is_user_in_db:
        reply_markup = keyboards.newbie_kb
    await bot.send_message(message.from_user.id, 'Ваша диаграмма!', reply_markup=reply_markup)
    os.remove(filename + '.png')
    await state.finish()


@dp.message_handler(commands=['buy', 'купить'])
async def start_buying_command(message: types.message):
    await types.ChatActions.typing()
    await BuyingState.waiting_for_number.set()
    await bot.send_message(message.from_user.id, '\n'.join(list_phrases['start_buying']),
                           reply_markup=ReplyKeyboardRemove())


async def phone_sent(message: types.message, state):
    await types.ChatActions.typing()
    try:
        phone = message.text
        checking_phone(phone)
        await state.update_data(phone=phone)
        await bot.send_message(message.from_user.id, str_phrases['correct_number'],
                               reply_markup=keyboards.cryptos_kb)
        await BuyingState.waiting_for_crypto.set()
    except WrongPhoneLength:
        await bot.send_message(message.from_user.id, str_phrases['not_full_phone'])
    except PhoneNotRussian:
        await bot.send_message(message.from_user.id, str_phrases['phone_not_russian'])
        await state.finish()
    except SomeTextInThePhone:
        await bot.send_message(message.from_user.id, str_phrases['not_only_digits'])


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
    await BuyingState.waiting_for_amount.set()


async def amount_for_buy_chosen(message: types.message, state):
    """"""

    try:
        chosen_amount = float(message.text)
        # todo: написать хрень которая чекает по балансу наш банк по выбранной криптовалюте.
        state_data = await state.get_data()
        chosen_crypto = state_data['chosen_crypto']
        phone = state_data['phone']
        rub_price = moneywagon.get_current_price(phrases.cryptos_abbreviations[chosen_crypto], 'RUB')
        rub_and_cop = round(round(rub_price, 2) * (chosen_amount + crypto_fees[chosen_crypto]), 2)
        link = None
        if not rub_and_cop.is_integer():
            link = qiwi_links_generator.create_bill(int(str(rub_and_cop).split('.')[0]),
                                                    int(str(rub_and_cop).split('.')[1]))
        else:
            link = qiwi_links_generator.create_bill(rub_and_cop, 0)
        headers = {
            'Authorization': 'Bearer ',
            "Content-Type": "application/json"
        }
        json_params = {
            'long_url': link

        }
        response = requests.post('https://api-ssl.bitly.com/v4/shorten', headers=headers,
                                 json=json_params).json()
        link = response['link']
        await types.ChatActions.typing()
        msg = f'Отлично, вы можете купить это количество {phrases.cryptos_abbreviations[chosen_crypto]}. Совершите перевод по {link} и нажмите на кнопку внизу, чтобы подтвердить перевод'
        await bot.send_message(message.from_user.id, msg, reply_markup=keyboards.payment_button)
    except ValueError:
        await types.ChatActions.typing(2)
        await bot.send_message(message.from_user.id, 'Вы должны написать число(без букв).')


@dp.message_handler()
async def process_text(message):
    """Делаем так, чтобы комманды были доступны с помощью клавиатуры и обычных фраз, а не только
    команд типа /команда"""

    if message.text.lower() == 'помощь':
        await process_help_command(message)
    if message.text.lower() == 'создать аккаунт':
        await process_create_command(message)
    if message.text.lower() == 'инфо об аккаунте':
        await process_account_command(message)
    if message.text.lower() == 'курсы валют💱':
        await start_price_command(message)
    if message.text.lower() == 'привязать почту📩':
        await start_email_command(message)
    if message.text.lower() == 'график стоимости📈':
        await start_graph_command(message)
    if message.text.lower() == 'купить криптовалюту💸':
        await start_buying_command(message)


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
    dispatcher.register_message_handler(phone_sent, state=BuyingState.waiting_for_number)
    dispatcher.register_message_handler(crypto_for_buy_chosen, state=BuyingState.waiting_for_crypto)
    dispatcher.register_message_handler(amount_for_buy_chosen, state=BuyingState.waiting_for_amount)


if __name__ == '__main__':
    register_handlers_price(dp)
    register_mail_handlers(dp)
    register_graph_handlers(dp)
    register_buy_handlers(dp)
    print('Bot is running now')
    executor.start_polling(dp)
