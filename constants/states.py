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


class CheckBalance(StatesGroup):
    waiting_for_crypto = State()
    wallet_is_bound = State()
    use_users_wallet = State()
    wallet_not_bound = State()


class SendTransaction(StatesGroup):
    waiting_for_crypto = State()
    waiting_for_secret_key = State()
    waiting_for_amount = State()
    waiting_for_wallet_to_send = State()


class CheckStatus(StatesGroup):
    waiting_for_crypto = State()
    waiting_for_tx_hash = State()


class ChoosePriceOperation(StatesGroup):
    waiting_for_variant = State()


class ChooseAccountOperation(StatesGroup):
    waiting_for_variant = State()


class ChooseCryptoOperation(StatesGroup):
    waiting_for_variant = State()


class NewsSubscribe(StatesGroup):
    waiting_for_choose = State()
