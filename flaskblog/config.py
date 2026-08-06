import os
from dotenv import load_dotenv

# Load variables from .env file (if present) so local dev works without
# manually exporting environment variables in every terminal session.
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
        )

    # Support DATABASE_URL from Render/Heroku; fix postgres:// prefix for SQLAlchemy
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = _db_url

    # ── Session / Cookie security ─────────────────────────────────────────────
    # On Render (HTTPS), the browser only sends cookies marked Secure.
    # SameSite=Lax prevents CSRF while still allowing normal navigation.
    SESSION_COOKIE_SECURE   = os.environ.get('SESSION_COOKIE_SECURE', 'True').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ── CSRF ──────────────────────────────────────────────────────────────────
    # Disable strict SSL Referer check — it breaks behind Render's reverse proxy
    # (ProxyFix in fast.py handles the real origin correctly instead).
    WTF_CSRF_SSL_STRICT = False

    # ── Mail (SMTP) ──────────────────────────────────────────────────────────
    # For LOCAL DEVELOPMENT: use Mailtrap (free fake inbox at mailtrap.io)
    #   MAIL_SERVER  = sandbox.smtp.mailtrap.io
    #   MAIL_PORT    = 2525
    #   Get USERNAME & PASSWORD from: mailtrap.io → Inboxes → SMTP Settings → Flask-Mail
    #
    # For PRODUCTION: use Gmail App Password or SendGrid
    #   MAIL_SERVER  = smtp.gmail.com
    #   MAIL_PORT    = 587
    MAIL_SERVER   = os.environ.get('MAIL_SERVER',   'sandbox.smtp.mailtrap.io')
    MAIL_PORT     = int(os.environ.get('MAIL_PORT', 2525))
    MAIL_USE_TLS  = os.environ.get('MAIL_USE_TLS',  'True').lower() == 'true'
    MAIL_USE_SSL  = os.environ.get('MAIL_USE_SSL',  'False').lower() == 'true'
    MAIL_USERNAME = os.environ.get('EMAIL_USER')
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')
    # Set to True to skip sending emails entirely (useful in unit tests)
    MAIL_SUPPRESS_SEND = os.environ.get('MAIL_SUPPRESS_SEND', 'False').lower() == 'true'