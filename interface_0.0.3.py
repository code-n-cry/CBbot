import aiogram
import keyboards
import phrases
import smtplib
import schedule
import checking_email
from db_helper import DbHelper

codes_db = DbHelper('codes.sqlite')
codes_db.create('main', ['id', 'code', 'email'])
accounts_db = DbHelper('accounts.sqlite')
accounts_db.create('accounts', ['id', 'email', 'wallet'])
bot = aiogram.Bot(token='1642386679:AAHwsU2ANqdAf2_od8EnUyi7RKrFoiUEQZs')
dp = aiogram.Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message):
    await bot.send_message(message.from_user.id, '\n'.join(phrases.hi_message),
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


@dp.message_handler(commands=['create'])
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
            code = checking_email.verify_email(mail)
            codes_db.insert('main', ['id', 'code', 'email'],
                            [str(message.from_user.id), str(code), f'"{mail}"'])
            await bot.send_message(message.from_user.id, phrases.code_sent)
        except IndexError:
            await bot.send_message(message.from_user.id, phrases.no_email)
        except smtplib.SMTPRecipientsRefused:
            await bot.send_message(message.from_user.id, phrases.not_full_email)
        except checking_email.EmailDoesNotExists:
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


@dp.message_handler(commands=['code'])
async def verifying_email(message):
    if list(filter(lambda user: user[0] == message.from_user.id,
                   accounts_db.select('accounts', 'id'))):
        try:
            if list(filter(lambda id: id[0] == message.from_user.id, codes_db.select('main', 'db'))):
                code = message.text.split(' ')[1]
                right_code = str(
                    codes_db.select_where('main', f'id={message.from_user.id}', 'code')[-1][0])
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


@dp.message_handler()
async def process_text(message):
    if message.text.lower() == 'помощь':
        await process_help_command(message)
    if message.text.lower() == 'создать аккаунт':
        await process_create_command(message)
    if message.text.lower() == 'инфо об аккаунте':
        await process_account_command(message)


if __name__ == '__main__':
    aiogram.utils.executor.start_polling(dp)
