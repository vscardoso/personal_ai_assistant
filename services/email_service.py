"""Simple SMTP email service used by the application.

Configuration (via env vars or .env):
- SMTP_HOST (required)
- SMTP_PORT (default 587)
- SMTP_USER (optional)
- SMTP_PASSWORD (optional)
- SMTP_USE_TLS (default true)
- FROM_EMAIL (default no-reply@example.com)
"""
import os
import smtplib
import logging
from email.message import EmailMessage
from typing import Optional, Dict

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

load_dotenv()
logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("1", "true", "yes")
FROM_EMAIL = os.getenv("FROM_EMAIL", "no-reply@example.com")

# templates folder (relative to project root -> app/templates)
TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "app", "templates")
env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=select_autoescape(["html", "xml"])
)


class EmailService:
    def __init__(self):
        if not SMTP_HOST:
            logger.warning("SMTP_HOST not configured. Emails will not be sent.")
            self.enabled = False
        else:
            self.enabled = True

    def _send(self, msg: EmailMessage) -> bool:
        try:
            if SMTP_USE_TLS:
                with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                    server.starttls()
                    if SMTP_USER and SMTP_PASSWORD:
                        server.login(SMTP_USER, SMTP_PASSWORD)
                    server.send_message(msg)
            else:
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=10) as server:
                    if SMTP_USER and SMTP_PASSWORD:
                        server.login(SMTP_USER, SMTP_PASSWORD)
                    server.send_message(msg)

            logger.info(f"Email sent to {msg['To']} (subject: {msg['Subject']})")
            return True
        except Exception as e:
            logger.exception(f"Failed to send email to {msg.get('To')}: {e}")
            return False

    def send_email(self, to_email: str, subject: str, body: str, html: Optional[str] = None) -> bool:
        """Send a simple email. Returns True on success, False otherwise."""
        if not self.enabled:
            logger.info(f"Email disabled - would send to {to_email} with subject '{subject}'")
            return False

        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        if html:
            msg.add_alternative(html, subtype="html")

        return self._send(msg)

    def send_templated_email(self, to_email: str, subject: str, template_name: str, context: Optional[Dict] = None) -> bool:
        """Render a Jinja2 template (both text and HTML) and send it."""
        if not self.enabled:
            logger.info(f"Email disabled - would send templated email to {to_email} subject '{subject}' template '{template_name}'")
            return False

        context = context or {}
        # try load html and text templates
        html = None
        text = None
        try:
            # HTML template (optional)
            tmpl_html = env.get_template(f"{template_name}.html")
            html = tmpl_html.render(**context)
        except Exception:
            html = None

        try:
            tmpl_txt = env.get_template(f"{template_name}.txt")
            text = tmpl_txt.render(**context)
        except Exception:
            text = None

        # Fallback body
        body = text or (html and "Por favor, veja o conteúdo HTML deste e-mail.") or ""

        msg = EmailMessage()
        msg["From"] = FROM_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        if html:
            msg.add_alternative(html, subtype="html")

        return self._send(msg)


email_service = EmailService()
