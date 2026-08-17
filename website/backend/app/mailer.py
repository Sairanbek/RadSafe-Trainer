import smtplib
import ssl
from email.mime.text import MIMEText

from app.config import settings


def _send(to_email: str, subject: str, body: str) -> None:
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as server:
        server.starttls(context=ssl.create_default_context())
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    body = (
        "Здравствуйте!\n\n"
        "Вы запросили сброс пароля на RST — RadSafe Trainer.\n"
        f"Перейдите по ссылке, чтобы задать новый пароль:\n{reset_link}\n\n"
        "Ссылка действительна 30 минут. Если вы не запрашивали сброс пароля, "
        "просто проигнорируйте это письмо."
    )
    _send(to_email, "RST — сброс пароля", body)


def send_verification_email(to_email: str, verify_link: str) -> None:
    body = (
        "Здравствуйте!\n\n"
        "Спасибо за регистрацию в RST — RadSafe Trainer.\n"
        f"Подтвердите свой email, перейдя по ссылке:\n{verify_link}\n\n"
        "Ссылка действительна 24 часа. Если вы не регистрировались — "
        "просто проигнорируйте это письмо."
    )
    _send(to_email, "RST — подтверждение email", body)


def send_source_change_alert(changed_sections: list[str]) -> None:
    sections_list = "\n".join(f"- {s}" for s in changed_sections)
    body = (
        "Ежемесячная проверка первоисточников на adilet.zan.kz нашла изменения "
        f"в следующих разделах:\n\n{sections_list}\n\n"
        "Текст документа изменился с прошлой проверки — нужно вручную сверить "
        "вопросы этих разделов с новым текстом и обновить неверные/устаревшие "
        "ответы. Подробности и ссылки — в website/backend/law_snapshots/."
    )
    _send(settings.smtp_from, "RST — изменения в первоисточниках", body)
