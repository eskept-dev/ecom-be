from app.core.celery import celery_app
from app.auth.services import send_activation_email
from app.user.models import User
from app.core.utils.logger import logger


@celery_app.task(name='send_activation_email_task')
def send_activation_email_task(user_id):
    logger.info(f"Sending activation email to user {user_id}")
    user = User.objects.get(id=user_id)
    send_activation_email(user)
    logger.info(f"Sent activation email to user {user_id}")
