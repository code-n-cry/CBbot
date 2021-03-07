import moneywagon

from states import GetPrice
from aiogram.utils import executor
from aiogram import Dispatcher, Bot
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from checking_email import EmailDoesNotExists, verify_email
from smtplib import SMTPRecipientsRefused
from db_helper import DbHelper
import keyboards
import phrases
import asyncio

codes_db = DbHelper('db/codes.sqlite')
codes_db.create('main', ['id', 'code', 'email'])
accounts_db = DbHelper('db/accounts.sqlite')
accounts_db.create('accounts', ['id', 'email', 'wallet'])
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
        await bot.answer_callback_query(call.id)
        await bot.send_message(call.from_user.id, '\n'.join(phrases.help_message),
                               reply_markup=keyboards.main_kb)


@dp.message_handler(commands=['помощь', 'help'])
async def process_help_command(message):
    await bot.send_message(message.from_user.id, '\n'.join(phrases.help_message),
                           reply_markup=keyboards.main_kb)


@dp.message_handler(commands=['create', 'создать'])
async def process_create_command(message):
    is_user_in_db = list(
        filter(lambda user: user[0] == message.from_user.id, accounts_db.select('accounts', 'id')))
    if is_user_in_db:
        await bot.send_message(message.from_user.id, phrases.already_registered)
    else:
        await bot.send_message(message.from_user.id, '\n'.join(phrases.creating_msg))


@dp.message_handler(commands=['email'])
async def processing_email(message):
    is_user_in_db = list(
        filter(lambda user: user[0] == message.from_user.id, accounts_db.select('accounts', 'id')))
    if is_user_in_db:
        try:
            mail = message.text.split(' ')[1]
            code = verify_email(mail)
            codes_db.insert('main', ['id', 'code', 'email'],
                            [str(message.from_user.id), str(code), f'"{mail}"'])
            await bot.send_message(message.from_user.id, phrases.code_sent)
        except IndexError:
            await bot.send_message(message.from_user.id, phrases.no_email)
        except SMTPRecipientsRefused:
            await bot.send_message(message.from_user.id, phrases.not_full_email)
        except EmailDoesNotExists:
            await bot.send_message(message.from_user.id, phrases.invalid_email)
    else:
        await bot.send_message(message.from_user.id, phrases.already_registered)


@dp.message_handler(commands=['account'])
async def process_account_command(message):
    is_user_in_db = list(
        filter(lambda user: user[0] == message.from_user.id, accounts_db.select('accounts', 'id')))
    if is_user_in_db:
        email = accounts_db.select_where('accounts', f'id={message.from_user.id}', 'email')[0][0]
        await bot.send_message(message.from_user.id, phrases.account_info(email))
    else:
        await bot.send_message(message.from_user.id, phrases.no_account)


@dp.message_handler(commands=['code', 'код'])
async def verifying_email(message):
    if not list(filter(lambda user: user[0] == message.from_user.id,
                       accounts_db.select('accounts', 'id'))):
        try:
            if list(filter(lambda id: id[0] == message.from_user.id, codes_db.select('main', 'id'))):
                code = message.text.split(' ')[1]
                right_code = str(
                    codes_db.select_where('main', f'id={message.from_user.id}', 'code')[-1][0])
                await asyncio.sleep(10)
                if code == right_code:
                    email = codes_db.select_where('main', f'id={message.from_user.id}', 'email')[-1][
                        0]
                    accounts_db.insert('accounts', ['id', 'email'],
                                       [str(message.from_user.id), f'"{email}"'])
                    await bot.send_message(message.from_user.id, '\n'.join(phrases.code_success))
                    codes_db.delete_where('main', f'id={str(message.from_user.id)}')
                else:
                    await bot.send_message(message.from_user.id, phrases.invalid_code)
            else:
                await bot.send_message(message.from_user.id, phrases.mail_not_specified)
        except IndexError:
            await bot.send_message(message.from_user.id, phrases.no_code)
    else:
        await bot.send_message(message.from_user.id, phrases.already_registered)


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
    await bot.send_message(message.from_user.id,
                           phrases.price_info(chosen_crypto['chosen_crypto'], fiat_to_genitive,
                                              price, chosen_fiat_code),
                           reply_markup=keyboards.main_kb)
    await state.finish()


@dp.message_handler()
async def process_text(message):
    if message.text.lower() == 'помощь':
        await process_help_command(message)
    if message.text.lower() == 'создать аккаунт':
        await process_create_command(message)
    if message.text.lower() == 'инфо об аккаунте':
        await process_account_command(message)
    if message.text.lower() == 'курсы валют':
        await start_price_command(message)


def register_handlers_price(dispatcher):
    dispatcher.register_message_handler(start_price_command, commands="price", state='*')
    dispatcher.register_message_handler(crypto_chosen, state=GetPrice.waiting_for_crypto)
    dispatcher.register_message_handler(fiat_chosen, state=GetPrice.waiting_for_fiat)


if __name__ == '__main__':
    register_handlers_price(dp)
    executor.start_polling(dp)
