import requests
import random
import datetime


class Qiwi:
    def __init__(self, token, phone):
        """
        Основной класс для взаимодействия с кошельком
        token - токен кошелька
        secret_key - secret key p2p транзакций
        phone - номер телефона (71234567890)
        """
        self.phone = phone
        self.token = token
        self.ses = requests.Session()
        self.ses.headers['Accept'] = 'application/json'
        self.ses.headers['authorization'] = 'Bearer ' + token
        self.ses.headers['Content-type'] = 'application / json'

    def get_account_info(self):
        """Получение информации об аккаунте"""
        r = self.ses.get('https://edge.qiwi.com/person-profile/v1/profile/current')
        return r.json()

    def get_balance(self):
        """Получение баланса"""
        r = self.ses.get(f'https://edge.qiwi.com/funding-sources/v2/persons/{self.phone}/accounts')
        return r.json()

    def get_all_history(self):
        """Получение всей истории(последние 50 транзакций)"""
        params = {'rows': 50}
        r = self.ses.get(f'https://edge.qiwi.com/payment-history/v2/persons/{self.phone}/payments',
                         params=params)
        return r.json()

    def get_specific_history(self, rows=50, operation='ALL', startDate=None, endDate=None,
                             nextTxnDate=None, nextTxnId=None):
        """Получение более детальной истории"""
        params = {'rows': rows, 'operation': operation}
        if startDate and endDate:
            params['startDate'] = startDate
            params['endDate'] = endDate
        if nextTxnDate and nextTxnId:
            params['nextTxnDate'] = nextTxnDate
            params['nextTxnId'] = nextTxnId
        r = self.ses.get(f'https://edge.qiwi.com/payment-history/v2/persons/{self.phone}/payments',
                         params=params)
        return r.json()

    def create_bill(self, rub=0, kop=0, cur=643):
        """Генерация ссылки для оплаты"""
        nickname = self.ses.get(f'https://edge.qiwi.com/qw-nicknames/v1/persons/{self.phone}/'
                                f'nickname').json()['nickname']
        link = f"https://qiwi.com/payment/form/99999?extra['account']={nickname}&amountInteger=" \
               f"{rub}&amountFraction={kop}&currency={cur}&blocked[0]=account&blocked[1]=" \
               f"sum&blocked[2]=comment&account&extra['accountType']=nickname "
        return link
