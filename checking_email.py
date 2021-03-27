import smtplib
import json
import random
from email.mime import multipart, text
from validate_email import validate_email
from exceptions import EmailDoesNotExists
from time import sleep

with open('static/json/general_bot_info.json', encoding='utf-8') as input_json:
    input_json = json.load(input_json)
    need_data = input_json['Email']


def send_message(email, msg_text):
    global need_data
    message = multipart.MIMEMultipart()
    message['From'] = need_data['email']
    message['To'] = email
    phrase = [f'Авторизация в CBbot']
    message['Subject'] = '\n'.join(phrase)
    message.attach(text.MIMEText(msg_text, 'plain'))
    sender = smtplib.SMTP_SSL('smtp.mail.yahoo.com', 465)
    sender.login(need_data['email'], need_data['password'])
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
