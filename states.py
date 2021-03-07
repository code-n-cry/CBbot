from aiogram.dispatcher.filters.state import State, StatesGroup


class GetPrice(StatesGroup):
    waiting_for_crypto = State()
    waiting_for_fiat = State()