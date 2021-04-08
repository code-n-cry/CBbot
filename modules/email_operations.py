import smtplib
import logging
import random
from email.mime import multipart, text
from validate_email import validate_email
from exceptions import EmailDoesNotExists
from time import sleep


class EmailOperations:
    """Класс для взаимодействий с электронной почтой. В каждой функции для отправки письма произ
    водится сон в течение 2.5 секунд, чтобы уменьшить вероятность попадания в спам"""

    def __init__(self, email: str, password: str):
        logging.basicConfig(filename='email.log',
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')
        self.email = email
        self.password = password
        self.sender = None

    def send_authorization_message(self, email_to: str, msg_text: str):
        try:
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
        except Exception as e:
            logging.error(str(e) + ' Auth', name='email')

    def send_buy_info(self, email_to: str, tx_code: str, crypto_currency: str, amount: int):
        try:
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
        except Exception as e:
            logging.error(str(e) + ' check', name='email')

    def verify_email(self, email: str, name: str):
        if validate_email(email, verify=True):
            code = str(random.randrange(100000, 999999))
            body = f'Доброго времени суток, {name}!\nТвой код верификации: {code}'
            self.send_authorization_message(email, body)
            return code
        raise EmailDoesNotExists
