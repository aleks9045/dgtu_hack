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
    email = MIMEText(f'''
        <div style="background-color: #2B2D31; border-radius:10px;">
        <h1 style="color: white; padding: 18px 0 0 20px;">Здравствуйте, {first_name} {last_name}</h1>
        <h3 style="color: white; padding: 15px 0 0 20px;">Вы были приглашены в команду {team_name}</h3>
        <p style="color: white; padding: 0 0 20px 20px;">Перейдите по ссылке, чтобы вступить в неё.<p>
        <p style="color: white; padding: 20px 0 20px 20px;">Ссылка: sdfadsfasdfasdfsadgasd<p>
        </div>''', "html")
    smtp_server.sendmail("Awesome Hackaton 2024", email_to, email.as_string())


@celery.task
def send_notification_delete(email_to: str, first_name: str, last_name: str, team_name: str):
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(MAIL_USERNAME, MAIL_PASSWORD)
    email = MIMEText(f'''
        <div style="background-color: #2B2D31; border-radius:10px;">
        <h1 style="color: white; padding: 18px 0 0 20px;">Здравствуйте, {first_name} {last_name}</h1>
        <h3 style="color: white; padding: 15px 0 20px 20px;">Вы были удалены из команды {team_name}</h3>
        </div>''', "html")
    smtp_server.sendmail(MAIL_USERNAME, email_to, email.as_string())
