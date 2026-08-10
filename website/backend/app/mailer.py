import smtplib
import ssl
from email.mime.text import MIMEText

from app.config import settings


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    body = (
        "Здравствуйте!\n\n"
        "Вы запросили сброс пароля на RST — RadSafe Trainer.\n"
        f"Перейдите по ссылке, чтобы задать новый пароль:\n{reset_link}\n\n"
        "Ссылка действительна 30 минут. Если вы не запрашивали сброс пароля, "
        "просто проигнорируйте это письмо."
    )
    msg = MIMEText(body)
    msg["Subject"] = "RST — сброс пароля"
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
