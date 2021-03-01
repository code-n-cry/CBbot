import aiogram
import keyboards
import phrases

bot = aiogram.Bot(token='')
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


@dp.message_handler()
async def process_text(message):
    if message.text.lower() == 'помощь':
        await bot.send_message(message.from_user.id, '\n'.join(phrases.help_message),
                               reply_markup=keyboards.main_kb)


if __name__ == '__main__':
    aiogram.utils.executor.start_polling(dp)
