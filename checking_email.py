import smtplib
from email.mime import multipart, text
from validate_email import validate_email
from exceptions import EmailDoesNotExists
from time import sleep
import random


def send_message(email, msg_text):
    message = multipart.MIMEMultipart()
    message['From'] = "cbbot.telegram@mail.ru"
    message['To'] = email
    phrase = [f'Авторизация в CBbot']
    message['Subject'] = '\n'.join(phrase)
    message.attach(text.MIMEText(msg_text, 'plain'))
    sender = smtplib.SMTP_SSL('smtp.mail.ru', 465)
    sender.login("", "")
    sleep(2.5)
    sender.send_message(message)
    sender.quit()


def verify_email(email, name):
    if validate_email(email, verify=True):
        code = str(random.randrange(100000, 999999))
        body = f'Доброго времени суток, {name}!\nТвой код верификации: {code}'
        send_message(email, body)
        return code
    raise EmailDoesNotExists
