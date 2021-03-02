hi_message = ['Привет 👋! Это CBbot(Crypto Burse bot).',
              'Наш бот позволяет проводить какие-либо операции с криптовалютами.',
              'Подробнее читай по команде "/help" или "/помощь"']
help_message = ['Помощь уже тут! Вот, что я могу:',
                '/create - создать аккаунт в системе CBbot',
                '/account - просмотреть информацию о своём аккаунте']
creating_msg = ['Вы решили создать аккаунт? Отлично! Вот доступные шаги:',
                '/email {ваш email} - привязать почту',
                '/code {код} - потвердить свою почту(доступно после команды /email)',
                'И обещаем: никаких рассылок!']
code_sent = 'Код выслан вам на почту!'
no_email = 'После /email введите вашу почту!'
invalid_email = "Такого адреса не сущесвует!\nПроверьте правильность написания"
not_full_email = "Введите адрес почты полностью!"
no_code = 'Не был введён код. Верификация отклонена.'
invalid_code = 'Неверный код! Верификация отклонена.'
code_success = ['Правильный код! Ваш e-mail зашифрован и внесён в базу данных.',
                'Теперь вы можете:',
                '① Привязать кошельки криптовалют к аккаунту(доступные валюты: Bitcoin, Litecoin, Ethereum, Dogecoin)',
                '② Привязать к аккаунту платёжные реквизиты']
already_registered = 'Этот e-mail уже зарегистрирован в нашей системе!'
no_account = 'Вы не зарегистрированы в нашей системе ☹!\nНо это легко исправить! Нужно всего лишь... /email'


def account_info(email):
    text = ['Отлично! Вы зарегистрированы в системе CBbot.',
            'Информация об аккаунте:',
            f'Электронная почта: {email}']
    return '\n'.join(text)
