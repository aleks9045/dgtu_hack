from celery import Celery
from config import MAIL_USERNAME, MAIL_PASSWORD, MAIL_FROM
import smtplib

celery = Celery('tasks', broker='redis://redis:6379')


@celery.task
def send_notification(email: str):
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(MAIL_USERNAME, MAIL_PASSWORD)
    smtp_server.sendmail(MAIL_USERNAME, email, "FV Kostill")