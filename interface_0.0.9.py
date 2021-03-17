import moneywagon
from math_operations import MathOperations
from states import GetPrice, GetEmail, BuildGraph
from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from checking_email import EmailDoesNotExists, verify_email
from smtplib import SMTPRecipientsRefused
from data import db_session
from data.verification import IsVerifying
from data.user import User
import keyboards
import time
import os
import phrases

print('DB initialization.....')
db_session.initialization('db/all_data.sqlite')
print('Bot starting...')
bot = Bot(token='')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


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
        await bot.send_message(call.from_user.id, '\n'.join(phrases.help_message),
                               reply_markup=reply_markup)


@dp.message_handler(commands=['помощь', 'help'])
async def process_help_command(message):
    reply_markup = keyboards.main_kb
    session = db_session.create_session()
    is_user_in_db = [user for user in session.query(User).filter(User.id == message.from_user.id)]
    if not is_user_in_db:
        reply_markup = keyboards.newbie_kb
    await bot.send_message(message.from_user.id, '\n'.join(phrases.help_message),
                           reply_markup=reply_markup)


@dp.message_handler(commands=['create', 'создать'])
async def process_create_command(message):
    db_sess = db_session.create_session()
    is_user_in_db = [user for user in db_sess.query(User).filter(User.id == message.from_user.id)]
    if is_user_in_db:
        await bot.send_message(message.from_user.id, phrases.already_registered)
    else:
        await bot.send_message(message.from_user.id, '\n'.join(phrases.creating_msg),
                               reply_markup=keyboards.email_kb)


@dp.message_handler(commands=['account', 'инфо', 'info'])
async def process_account_command(message):
    db_sess = db_session.create_session()
    is_user_in_db = [user for user in db_sess.query(User).filter(User.id == message.from_user.id)]
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
        await bot.send_message(message.from_user.id, phrases.no_account)


@dp.message_handler(commands=['email', 'почта'])
async def start_email_command(message):
    db_sess = db_session.create_session()
    is_user_in_db = [user for user in db_sess.query(User).filter(User.id == message.from_user.id)]
    if not is_user_in_db:
        await bot.send_message(message.from_user.id, phrases.send_me_email)
        await GetEmail.waiting_for_email.set()
        return
    await bot.send_message(message.from_user.id, phrases.already_registered)


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
            await bot.send_message(message.from_user.id, phrases.code_sent, reply_markup=None)
            await bot.send_message(message.from_user.id, phrases.send_code_next, reply_markup=None)
            await GetEmail.next()
        else:
            await bot.send_message(message.from_user.id, phrases.this_email_used)
    except EmailDoesNotExists:
        await bot.send_message(message.from_user.id, phrases.invalid_email,
                               reply_markup=keyboards.newbie_kb)
        state.finish()
    except SMTPRecipientsRefused:
        await bot.send_message(message.from_user.id, phrases.invalid_email,
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
                await bot.send_message(message.from_user.id, '\n'.join(phrases.code_success),
                                       reply_markup=keyboards.main_kb)
                session.query(IsVerifying).filter(
                    IsVerifying.id == message.from_user.id).delete()
                session.commit()
                await state.finish()
            else:
                await bot.send_message(message.from_user.id, phrases.invalid_code,
                                       reply_markup=keyboards.newbie_kb)
                state.finish()
        else:
            await bot.send_message(message.from_user.id, phrases.mail_not_specified,
                                   reply_markup=keyboards.newbie_kb)
            state.finish()
    except ValueError:
        await bot.send_message(message.from_user.id, phrases.invalid_code,
                               reply_markup=keyboards.newbie_kb)
        state.finish()


@dp.message_handler(commands=['price', 'курс'])
async def start_price_command(message):
    keyboard = keyboards.cryptos_kb
    await bot.send_message(message.from_user.id, 'Выберите валюту из предложенных',
                           reply_markup=keyboard)
    await GetPrice.waiting_for_crypto.set()


async def crypto_chosen(message, state):
    if message.text.capitalize() not in phrases.available_crypto:
        await bot.send_message(message.from_user.id, 'Пожалуйста, выбирайте из предложенных валют')
        return
    await state.update_data(chosen_crypto=message.text.capitalize())
    await GetPrice.next()
    await bot.send_message(message.from_user.id, 'К какой валюте привести?',
                           reply_markup=keyboards.fiat_kb)


async def fiat_chosen(message, state):
    if message.text.lower() not in phrases.available_fiat:
        await bot.send_message(message.from_user.id, 'Пожалуйста, выбирайте из предложенных валют')
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
    await bot.send_message(message.from_user.id,
                           phrases.price_info(chosen_crypto['chosen_crypto'], fiat_to_genitive,
                                              price, chosen_fiat_code),
                           reply_markup=reply_markup)
    await state.finish()


@dp.message_handler(commands=['graph', 'график'])
async def start_graph_command(message):
    keyboard = keyboards.cryptos_kb
    await BuildGraph.waiting_for_crypto.set()
    await bot.send_message(message.from_user.id, 'Выберите валюту из предложенных',
                           reply_markup=keyboard)


async def crypto_for_graph_chosen(message, state):
    if message.text.capitalize() not in phrases.available_crypto:
        await bot.send_message(message.from_user.id, 'Пожалуйста, выбирайте из предложенных валют')
        return
    chosen_crypto_code = phrases.cryptos_abbreviations[message.text.capitalize()]
    await bot.send_message(message.from_user.id, 'К какой валюте привести?',
                           reply_markup=keyboards.fiat_kb)
    await state.update_data(chosen_crypto=chosen_crypto_code)
    await BuildGraph.next()


async def fiat_for_graph_chosen(message, state):
    if message.text.lower() not in phrases.available_fiat:
        await bot.send_message(message.from_user.id, 'Пожалуйста, выбирайте из предложенных валют')
        return
    chosen_fiat_code = phrases.fiats_abbreviations[message.text.lower()]
    await bot.send_message(message.from_user.id,
                           'Отлично! Теперь выберите период, за который отобразить цену',
                           reply_markup=keyboards.periods_kb)
    await state.update_data(chosen_fiat=chosen_fiat_code)
    await BuildGraph.next()


async def period_for_graph_chosen(message, state):
    session = db_session.create_session()
    if message.text.capitalize() not in phrases.available_periods:
        await bot.send_message(message.from_user.id,
                               'Пожалуйста, выбирайте из предложенных периодов')
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
    build_me_plot = MathOperations(chosen_period, crypto_and_fiat['chosen_crypto'],
                                   crypto_and_fiat['chosen_fiat'], filename)
    build_me_plot.main()
    await types.ChatActions.upload_photo()
    media = types.MediaGroup()
    media.attach_photo(types.InputFile(filename + '.png'))
    await message.reply_media_group(media=media)
    reply_markup = keyboards.main_kb
    is_user_in_db = [user for user in
                     session.query(User).filter(User.id == message.from_user.id)]
    if not is_user_in_db:
        reply_markup = keyboards.newbie_kb
    await bot.send_message(message.from_user.id, 'Ваша диаграмма!',  reply_markup=reply_markup)
    os.remove(filename + '.png')
    await state.finish()


@dp.message_handler()
async def process_text(message):
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


if __name__ == '__main__':
    register_handlers_price(dp)
    register_mail_handlers(dp)
    register_graph_handlers(dp)
    print('bot running')
    executor.start_polling(dp)
