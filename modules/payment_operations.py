import requests
import random
import datetime


class PaymentOperations:
    """Класс для всяческих операций с фиатной валютой, в качестве платформы используется Qiwi"""

    def __init__(self, token: str, phone: str):
        """
        Основной класс для взаимодействия с кошельком;
        token - токен кошелька
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
        response = self.ses.get('https://edge.qiwi.com/person-profile/v1/profile/current')
        return response.json()

    def get_balance(self):
        """Получение баланса"""
        response = self.ses.get(
            f'https://edge.qiwi.com/funding-sources/v2/persons/{self.phone}/accounts')
        return response.json()

    def get_all_history(self):
        """Получение всей истории(последние 50 транзакций)"""
        params = {'rows': 50}
        response = self.ses.get(
            f'https://edge.qiwi.com/payment-history/v2/persons/{self.phone}/payments', params=params)
        return response.json()

    def get_specific_history(self, rows=50, operation='ALL', start_date=None, end_date=None,
                             next_txn_date=None, next_txn_id=None):
        """Получение детальной истории(определённой транзакции)"""
        params = {'rows': rows, 'operation': operation}
        if start_date and end_date:
            params['startDate'] = start_date
            params['endDate'] = end_date
        if next_txn_date and next_txn_id:
            params['nextTxnDate'] = next_txn_date
            params['nextTxnId'] = next_txn_id
        response = self.ses.get(
            f'https://edge.qiwi.com/payment-history/v2/persons/{self.phone}/payments', params=params)
        return response.json()

    def create_bill(self, rub=0, kop=0, cur=643):
        """Генерация ссылки для оплаты"""
        nickname = self.ses.get(f'https://edge.qiwi.com/qw-nicknames/v1/persons/{self.phone}/nickname').json()['nickname']

        link = f"https://qiwi.com/payment/form/99999?extra['account']={nickname}&amountInteger=" +\
               f"{rub}&amountFraction={kop}&currency={cur}&blocked[0]=account&blocked[1]=" +\
               f"sum&blocked[2]=comment&account&extra['accountType']=nickname "
        return link
