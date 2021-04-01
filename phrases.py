from aiogram.utils.markdown import bold


def start_phrase(name):
    return '\n'.join([f'Привет, {name} 👋! ',
                      'Это CBbot(Crypto Burse bot). Он позволяет проводить какие-либо операции с криптовалютами.',
                      'Подробнее по команде "/help"'])


def all_okay(chosen_crypto: str, link: str):
    lst = [f'Отлично, вы можете купить это количество {cryptos_abbreviations[chosen_crypto]}.',
           f'Совершите перевод по {link} и нажмите на кнопку внизу, чтобы подтвердить перевод']
    return '\n'.join(lst)


def price_info(crypto: str, fiat: str, price: float, fiat_code: str):
    price = '{0:,}'.format(price).replace(',', ' ')
    return f'Текущий курс криптовалюты {crypto} к {fiat}: {price} {fiat_code}'


def account_info(btc_wal=False, ltc_wal=False, doge_wal=False, eth_wal=False):
    btc_wal_verified = 'Bitcoin-кошелёк: привязан' if btc_wal else 'Bitcoin-кошелёк не привязан'
    ltc_wal_verified = 'Litecoin-кошелёк: привязан' if ltc_wal else 'Litecoin-кошелёк не привязан'
    doge_wal_verified = 'Dogecoin-кошелёк: привязан' if doge_wal else 'Dogecoin-кошелёк не привязан'
    eth_wal_verified = 'Ethereum-кошелёк: привязан' if eth_wal else 'Ethereum-кошелёк не привязан'
    text = ['Отлично! Вы зарегистрированы в системе CBbot.',
            'Информация об аккаунте:', f'Электронная почта: подтверждена',
            btc_wal_verified, ltc_wal_verified, doge_wal_verified, eth_wal_verified]
    return '\n'.join(text)


def wallet_info(address: str, private: str, crypto_abbreviation: str):
    msg_text = [f'Адрес вашего {crypto_abbreviation}-кошелька: ' + bold(f'{address}'),
                f'Секретный ключ: ' + bold(f'{private}'),
                bold(
                    'Обязательно сохраните секретный ключ ! Он не будет в базе данных, но необходим для транзакций')]
    return '\n'.join(msg_text)


available_crypto = ['Bitcoin', 'Litecoin', 'Ethereum', 'Dogecoin']
available_fiat = ['рубль', 'доллар сша', 'евро']
available_periods = ['Неделя', 'Месяц', 'Год', 'Пять лет']
fiats_for_buttons = ['Рубль', 'Доллар США', 'Евро']
available_variants = ['Хочу сгенерировать себе кошелёк🖨️', 'Хочу привязать собственный📝']
cryptos_abbreviations = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Litecoin': 'LTC',
    'Dogecoin': 'DOGE'
}
abbreviations_to_crypto = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'LTC': 'litecoin',
    'DOGE': 'dogecoin'
}
fiats_abbreviations = {
    'рубль': 'RUB',
    'доллар сша': 'USD',
    'евро': 'EUR'
}
fiats_genitive = {
    'рубль': 'Рублю',
    'доллар сша': 'Доллару США',
    'евро': 'Евро'
}
