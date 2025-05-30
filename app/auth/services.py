from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from app.auth.enums import VerificationTypeEnum
from app.core import settings
from app.user.models import User


def send_verification_email_for_sign_up(user: User):
    email_template = 'email/verification_sign_up.html'
    email_subject = 'Activate your account'
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = [user.email]
    
    activation_url = (
        f"{settings.FRONTEND_URL}"
        f"/auth/sign-up?step=activate-account"
        f"&activation_code={user.activation_code}"
    )
    email_context = { 'activation_url': activation_url }

    html_content = render_to_string(email_template, email_context)

    email = EmailMultiAlternatives( 
        email_subject,
        '',
        email_from,
        email_to
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
