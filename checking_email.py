import smtplib
from email.mime import multipart, text
from validate_email import validate_email
import random


class EmailDoesNotExists(Exception):
    pass


def send_message(email, msg_text):
    message = multipart.MIMEMultipart()
    message['From'] = "cbot.telegramm@yandex.ru"
    message['To'] = email
    message['Subject'] = 'Подтвердите ваш адрес электронной почты'
    message.attach(text.MIMEText(msg_text, 'plain'))
    sender = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    sender.login("cbot.telegramm@yandex.ru", "aaaaaaa1N!")
    sender.send_message(message)
    sender.quit()


def verify_email(email):
    if validate_email(email, verify=True):
        code = str(random.randrange(100000, 999999))
        body = f'Код верификации: {code}'
        send_message(email, body)
        return code
    raise EmailDoesNotExists
