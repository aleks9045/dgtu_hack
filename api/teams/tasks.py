from celery import Celery
from config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM
import smtplib
from email.mime.text import MIMEText

celery = Celery('tasks', broker='redis://redis:6379')

@celery.task
def send_notification_add(email_to: str, first_name: str, last_name: str, team_name: str):
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(MAIL_USERNAME, MAIL_PASSWORD)
    email = MIMEText(
        '<div style="color: #2B2D31;">'
        f'<h1 style="color: white;">Здравствуйте, {first_name} {last_name}</h1>'
        f'<h3 style="color: white;">Вы были приглашены в команду {team_name}</h3>',
        f'<p>Перейдите по ссылке, чтобы согласиться или отказаться вступить в неё.<p>'
        '</div>'
        'html')
    smtp_server.sendmail(MAIL_USERNAME, email_to, email.as_string())

@celery.task
def send_notification_delete(email_to: str, first_name: str, last_name: str, team_name: str):
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(MAIL_USERNAME, MAIL_PASSWORD)
    email = MIMEText(
        f'<h1 style="color: red;">Здравствуйте, {first_name} {last_name}</h1>'
        f'<h3 style="color: blue;">Вы были удалены из команды {team_name}</h3>',
        'html')
    smtp_server.sendmail(MAIL_USERNAME, email_to, email.as_string())