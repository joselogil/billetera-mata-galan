"""
Email configuration for Gmail SMTP
Environment variables required:
- EMAIL_USER: Gmail address (e.g., your.email@gmail.com)
- EMAIL_PASSWORD: Gmail App Password (NOT regular password!)
- EMAIL_FROM_NAME: Display name for sender (optional, defaults to "Billetera Mata Galán")
"""

import os
from flask_mail import Mail, Message

# Email configuration
EMAIL_CONFIG = {
    'MAIL_SERVER': 'smtp.gmail.com',
    'MAIL_PORT': 587,
    'MAIL_USE_TLS': True,
    'MAIL_USE_SSL': False,
    'MAIL_USERNAME': os.environ.get('EMAIL_USER'),
    'MAIL_PASSWORD': os.environ.get('EMAIL_PASSWORD'),
    'MAIL_DEFAULT_SENDER': (
        os.environ.get('EMAIL_FROM_NAME', 'Billetera Mata Galán'),
        os.environ.get('EMAIL_USER')
    )
}

def init_mail(app):
    """
    Initialize Flask-Mail with the app
    Usage: mail = init_mail(app)
    """
    # Update app config
    app.config.update(EMAIL_CONFIG)

    # Create Mail instance
    mail = Mail(app)

    return mail

def validate_email_config():
    """
    Validates that required email environment variables are set
    Returns: (is_valid, error_message)
    """
    email_user = os.environ.get('EMAIL_USER')
    email_password = os.environ.get('EMAIL_PASSWORD')

    if not email_user:
        return False, "EMAIL_USER environment variable not set"

    if not email_password:
        return False, "EMAIL_PASSWORD environment variable not set"

    if '@' not in email_user:
        return False, f"EMAIL_USER is not a valid email: {email_user}"

    return True, "Email configuration is valid"
