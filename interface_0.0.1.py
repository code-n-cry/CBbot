import aiogram

bot = aiogram.Bot(token='')
dp = aiogram.Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def process_start_command(message):
    await bot.send_message(message.from_user.id, "CBbot")


if __name__ == '__main__':
    aiogram.utils.executor.start_polling(dp)