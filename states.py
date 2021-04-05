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


class BuyingState(StatesGroup):
    waiting_for_crypto = State()
    waiting_for_amount = State()
    waiting_for_wallet = State()
    wallet_sent = State()


class BindWallet(StatesGroup):
    waiting_for_crypto = State()
    bind_again_or_no = State()
    waiting_for_variant = State()
    waiting_for_wallet = State()
