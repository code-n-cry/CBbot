import smtplib
import json
import random
from email.mime import multipart, text
from validate_email import validate_email
from exceptions import EmailDoesNotExists
from time import sleep


class EmailOperations:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.sender = None

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

    def send_buy_info(self, email_to: str, tx_code: str, crypto_currency: str, amount: int):
        message = multipart.MIMEMultipart()
        message['From'] = self.email
        message['To'] = email_to
        phrase = [f'Уведомление о покупке с кодом {tx_code}']
        message['Subject'] = '\n'.join(phrase)
        msg_text = f""""С вашего аккаунта в системе CBbot совершена покупка {amount}
                    {crypto_currency}"""
        message.attach(text.MIMEText(msg_text, 'plain'))
        self.sender = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
        self.sender.login(self.email, self.password)
        sleep(2.5)
        self.sender.send_message(message)
        self.sender.quit()

    def verify_email(self, email: str, name: str):
        if validate_email(email, verify=True):
            code = str(random.randrange(100000, 999999))
            body = f'Доброго времени суток, {name}!\nТвой код верификации: {code}'
            self.send_authorization_message(email, body)
            return code
        raise EmailDoesNotExists
