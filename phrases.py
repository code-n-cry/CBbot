def start_phrase(name):
    return '\n'.join([f'Привет, {name} 👋! ',
                      'Это CBbot(Crypto Burse bot). Он позволяет проводить какие-либо операции с криптовалютами.',
                      'Подробнеепо команде "/help"'])


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


code_success = ['Правильный код! Ваш e-mail зашифрован и внесён в базу данных.',
                'Теперь вы можете:',
                '① Привязать кошельки криптовалют к аккаунту(доступные валюты: Bitcoin, Litecoin, Ethereum, Dogecoin)',
                '② Привязать к аккаунту платёжные реквизиты']
help_message = ['Помощь уже тут! Вот, что я могу:',
                '/create - создать аккаунт в системе CBbot',
                '/account - просмотреть информацию о своём аккаунте']
creating_msg = ['Вы решили создать аккаунт? Отлично! Вот доступные шаги:',
                '/email {ваш email} - привязать почту',
                '/code {код} - потвердить свою почту(доступно после команды /email)',
                'И обещаем: никаких рассылок!']
available_crypto = ['Bitcoin', 'Litecoin', 'Ethereum', 'Dogecoin']
available_fiat = ['рубль', 'доллар сша', 'евро']
available_periods = ['Неделя', 'Месяц', 'Год', 'Пять лет']
fiats_for_buttons = ['Рубль', 'Доллар США', 'Евро']
cryptos_abbreviations = {
    'Bitcoin': 'BTC',
    'Ethereum': 'ETH',
    'Litecoin': 'LTC',
    'Dogecoin': 'DOGE'
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
code_sent = 'Код выслан вам на почту!\nНе забудьте проверить папку "спам"'
no_email = 'После /email введите вашу почту!'
invalid_email = "Такого адреса не сущесвует!\nПроверьте правильность написания"
not_full_email = "Введите адрес почты полностью!"
no_code = 'Не был введён код. Верификация отклонена.'
invalid_code = 'Неверный код! Верификация отклонена.'
send_me_email = 'Введи и отправь сообщение с адресом своей электронной почты!'
already_registered = 'Вы уже зарегистрированы в нашей системе!'
no_account = 'Вы не зарегистрированы в нашей системе ☹!\nНо это легко исправить! Нужно всего лишь... /email'
mail_not_specified = 'Вы ещё не ввели email для отправки кода!'
send_code_next = 'В следующем сообщении введите код без других символов!'
this_email_used = 'На этот адрес почты уже зарегистрирован аккаунт!'
