import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import random


def send_message(mail, text):
    msg = MIMEMultipart()
    msg['From'] = "cbot.telegramm@yandex.ru"
    msg['To'] = mail
    msg['Subject'] = 'Подтвердите ваш адрес электронной почты'
    msg.attach(MIMEText(text, 'plain'))
    sender = smtplib.SMTP_SSL('smtp.yandex.ru', 465)
    sender.login("", "")
    sender.send_message(msg)
    sender.quit()


def verify_email():
    code = str(random.randrange(100000, 999999))
    body = f'Код верификации: {code}'
    send_message('zhuravlyov.maksimka@yandex.ru', body)
    if пока нету == code:
        send_message('zhuravlyov.maksimka@yandex.ru', 'Успешно')
        return True
    return False