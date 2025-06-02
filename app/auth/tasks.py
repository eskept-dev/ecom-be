from app.core.celery import celery_app
from app.auth import services as auth_services
from app.user.models import User
from app.core.utils.logger import logger


@celery_app.task(name='auth.tasks.send_verification_email_for_sign_up_task')
def send_verification_email_for_sign_up_task(user_id):
    logger.info(f"Sending verification email for sign up to user #{user_id}")
    user = User.objects.get(id=user_id)
    auth_services.send_verification_email_for_sign_up_brevo(user)
    logger.info(f"Sent verification email for sign up to user #{user_id}")


@celery_app.task(name='auth.tasks.send_sign_in_email_task')
def send_sign_in_email_task(user_id):
    logger.info(f"Sending sign in email to user #{user_id}")
    user = User.objects.get(id=user_id)
    auth_services.send_sign_in_email(user)
    logger.info(f"Sent sign in email to user #{user_id}")


@celery_app.task(name='auth.tasks.send_reset_password_email_task')
def send_reset_password_email_task(user_id):
    logger.info(f"Sending reset password email to user #{user_id}")
    user = User.objects.get(id=user_id)
    auth_services.send_reset_password_email(user)
    logger.info(f"Sent reset password email to user #{user_id}")
