import smtplib
from email.message import EmailMessage

from app.core.config import settings


async def send_verification_email(
    *,
    to_email: str,
    verification_link: str,
):
    msg = EmailMessage()
    msg["Subject"] = "Verify your email address"
    msg["From"] = "noreply@yourapp.com"
    msg["To"] = to_email
    msg.set_content(f"""
        Please verify your email address by clicking the link below:
        {verification_link}
        """)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)


async def send_reset_email(
    *,
    to_email: str,
    reset_link: str,
):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request"
    msg["From"] = "noreply@yourapp.com"
    msg["To"] = to_email
    msg.set_content(f"""
        You have requested a password reset. Please click the link below to reset your password:
        {reset_link}
        """)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
