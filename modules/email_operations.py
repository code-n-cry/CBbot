import smtplib
import random
import requests
from email.mime import multipart, text
from constants.exceptions import EmailDoesNotExists, EmailVerifyRequestsExpired
from time import sleep


class EmailOperations:
    """Класс для взаимодействий с электронной почтой. В каждой функции для отправки письма произ
    водится сон в течение 2.5 секунд, чтобы уменьшить вероятность попадания в спам"""

    def __init__(self, email: str, password: str, api_key: str):
        self.email = email
        self.password = password
        self.sender = None
        self.verifying_url = 'https://emailvalidation.abstractapi.com/v1/'
        self.verifying_api_key = api_key

    def send_authorization_message(self, email_to: str, msg_text: str):
        message = multipart.MIMEMultipart()
        message['From'] = self.email
        message['To'] = email_to
        phrase = ['Авторизация в CBbot']
        message['Subject'] = '\n'.join(phrase)
        message.attach(text.MIMEText(msg_text, 'plain'))
        self.sender = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        self.sender.login(self.email, self.password)
        sleep(2.5)
        self.sender.send_message(message)
        self.sender.quit()

    def send_buy_info(self, email_to: str, tx_code: str, crypto_currency: str, amount: int,
                      tx_hash: str):
        message = multipart.MIMEMultipart()
        message['From'] = self.email
        message['To'] = email_to
        phrase = [f'Уведомление о покупке с кодом {tx_code}']
        message['Subject'] = '\n'.join(phrase)
        msg_text = [f'С вашего аккаунта в CBbot совершена покупка {amount} {crypto_currency}',
                    f'ID транзакции в сети {crypto_currency}: {tx_hash}']
        message.attach(text.MIMEText('\n'.join(msg_text), 'plain'))
        self.sender = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        self.sender.login(self.email, self.password)
        sleep(2.5)
        self.sender.send_message(message)
        self.sender.quit()

    def validate_email(self, email: str):
        request_params = {
            'api_key': self.verifying_api_key,
            'email': email
        }
        json_response = requests.get(self.verifying_url, params=request_params).json()
        try:
            if json_response['deliverability'] == 'DELIVERABLE':
                return True
            return False
        except KeyError:
            raise EmailVerifyRequestsExpired

    def verify_email(self, email: str, name: str):
        print(email, name)
        try:
            if self.validate_email(email):
                code = str(random.randrange(100000, 999999))
                body = f'Доброго времени суток, {name}!\nТвой код верификации: {code}'
                self.send_authorization_message(email, body)
                return code
            raise EmailDoesNotExists
        except EmailVerifyRequestsExpired:
            return False
