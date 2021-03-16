from aiogram.dispatcher.filters.state import State, StatesGroup


class GetPrice(StatesGroup):
    waiting_for_crypto = State()
    waiting_for_fiat = State()


class GetEmail(StatesGroup):
    waiting_for_email = State()
    waiting_for_code = State()


class BuildGraph(StatesGroup):
    waiting_for_crypto = State()
    waiting_for_fiat = State()
    waiting_for_period = State()
