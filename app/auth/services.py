from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from app.core import settings
from app.user.models import User


def send_activation_email(user: User):
    email_template = 'email/activation.html'
    email_subject = 'Activate your account'
    email_from = settings.DEFAULT_FROM_EMAIL

    activation_url = f"{settings.FRONTEND_URL}/activate?activation_code={user.activation_code}"
    email_context = { 'activation_url': activation_url }
    email_to = [user.email]

    html_content = render_to_string(email_template, email_context)

    email = EmailMultiAlternatives(
        email_subject,
        '',
        email_from,
        email_to
    )
    email.attach_alternative(html_content, "text/html")
    email.send()


def send_login_email(user: User):
    email_template = 'email/sign_in.html'       
    email_subject = 'Sign in to your Eskept account'
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = [user.email]

    sign_in_url = f"{settings.FRONTEND_URL}/sign-in-via-email?token={user.activation_code}"
    email_context = { 'sign_in_url': sign_in_url }
    
    html_content = render_to_string(email_template, email_context)
    
    
    
