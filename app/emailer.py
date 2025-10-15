import smtplib
from email.message import EmailMessage
from typing import Dict
from .settings import settings

def send_email(subject: str, body: str) -> Dict[str, str]:
    if not settings.EMAIL_ENABLED:
        return {"status": "disabled"}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = settings.EMAIL_TO
    msg.set_content(body)

    try:
        if settings.SMTP_TLS:
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT, timeout=20)

        if settings.SMTP_USER:
            server.login(settings.SMTP_USER, settings.SMTP_PASS)

        server.send_message(msg)
        server.quit()
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
