from __future__ import annotations
import logging
import smtplib
from email.message import EmailMessage
from app.core.config import settings

log = logging.getLogger('omen.email')

def send_notification_email(to: str, subject: str, body: str) -> bool:
    if not settings.smtp_host or not settings.smtp_user or not settings.smtp_password:
        log.info('SMTP not configured; in-app notification remains the source of truth')
        return False
    message = EmailMessage(); message['Subject']=subject; message['From']=settings.smtp_user; message['To']=to; message.set_content(body)
    with smtplib.SMTP(settings.smtp_host, int(settings.smtp_port or 587)) as server:
        server.starttls(); server.login(settings.smtp_user, settings.smtp_password); server.send_message(message)
    return True
