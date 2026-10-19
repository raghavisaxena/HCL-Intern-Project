import os
import smtplib
import ssl
import time
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL

def _clean(text: str) -> str:
    return text.replace("**", "").replace("`", "")


def _send(to_email: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True on success, False on failure.
    Never raises, so an email problem can't break the ticket pipeline."""
    sender = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_APP_PASSWORD")

    if not sender or not password:
        print("[email_service] EMAIL_ADDRESS / EMAIL_APP_PASSWORD missing in .env")
        return False

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    last_error = None
    for attempt in range(1, 4):  # up to 3 tries
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context, timeout=15) as server:
                server.login(sender, password)
                server.send_message(msg)
            print(f"[email_service] Sent '{subject}' to {to_email} (attempt {attempt})")
            return True
        except Exception as e:
            last_error = e
            print(f"[email_service] Attempt {attempt} failed: {e}")
            time.sleep(1)

    print(f"[email_service] Giving up on {to_email}: {last_error}")
    return False


def send_acknowledgment_email(to_email: str, ticket_text: str) -> bool:
    subject = "We've received your IT ticket"
    body = (
        "Hello,\n\n"
        "We've received your ticket and our assistant is analyzing it now.\n\n"
        f"Your issue:\n{ticket_text}\n\n"
        "Quick tip while you wait: restart the affected application or device "
        "and check that you're connected to the network.\n\n"
        "You'll get a follow-up email shortly with the full resolution.\n\n"
        "- IT Incident Ticket Assistant"
    )
    return _send(to_email, subject, body)


def send_resolution_email(
    to_email: str,
    ticket_text: str,
    resolution: str,
    diagnostics: list[str] | None = None,
) -> bool:
    subject = "Resolution for your IT ticket"
    parts = [
        "Hello,\n",
        f"Your issue:\n{ticket_text}\n",
        f"Recommended resolution:\n{_clean(resolution)}\n",
    ]
    if diagnostics:
        parts.append("Automated diagnostics we ran:")
        parts.extend(f"  - {line}" for line in diagnostics)
        parts.append("")
    parts.append("- IT Incident Ticket Assistant")
    return _send(to_email, subject, "\n".join(parts))