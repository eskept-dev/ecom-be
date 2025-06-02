from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives, EmailMessage
from django.contrib.auth.hashers import check_password

from rest_framework_simplejwt.tokens import RefreshToken

from app.core import settings
from app.core.utils.logger import logger
from app.user.models import User
from app.core.sendgrid_client import sendgrid_client


def authenticate(email: str, password: str):
    user = User.objects.filter(email=email).first()
    if not user:
        return None

    if not check_password(password, user.password):
        return None

    return user


# ===============================
# Sign Up
# ===============================
def send_verification_email_for_sign_up(user: User):
    email_template = "email/verification_sign_up.html"
    email_subject = "Activate your account"
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = user.email

    activation_url = (
        f"{settings.FRONTEND_URL}"
        f"/en/auth/sign-up?step=activate-account"
        f"&activation_code={user.activation_code}"
    )
    email_context = {"activation_url": activation_url}

    html_content = render_to_string(email_template, email_context)

    sendgrid_client.send_email(
        to_emails=email_to,
        subject=email_subject,
        html_content=html_content,
        from_email=email_from,
    )


# ===============================
# Sign In
# ===============================
def send_sign_in_email(user: User):
    email_template = "email/sign_in_by_email.html"
    email_subject = "Sign in to your Eskept account"
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = [user.email]

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    sign_in_url = (
        f"{settings.FRONTEND_URL}"
        f"/en/auth/sign-in?step=verify-token"
        f"&access_token={access_token}"
    )
    email_context = {"sign_in_url": sign_in_url}

    html_content = render_to_string(email_template, email_context)

    sendgrid_client.send_email(
        to_emails=email_to,
        subject=email_subject,
        html_content=html_content,
        from_email=email_from,
    )


# ===============================
# Reset Password
# ===============================
def send_reset_password_email(user: User):
    email_template = "email/reset_password.html"
    email_subject = "Reset your password"
    email_from = settings.DEFAULT_FROM_EMAIL
    email_to = user.email

    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)

    reset_password_url = (
        f"{settings.FRONTEND_URL}"
        f"/en/auth/reset-password?step=verify-token"
        f"&access_token={access_token}"
    )
    email_context = {"reset_password_url": reset_password_url}

    html_content = render_to_string(email_template, email_context)

    sendgrid_client.send_email(
        to_emails=email_to,
        subject=email_subject,
        html_content=html_content,
        from_email=email_from,
    )


def reset_password(user: User, password: str):
    user.set_password(password)
    user.save()
