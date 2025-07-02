from app.core.celery import celery_app
from app.payment.services.process_payment import process_payment
from app.payment.models import PaymentTransaction


@celery_app.task(name='payment.tasks.process_payment_task')
def process_payment_task(payment_transaction_id):
    process_payment(payment_transaction_id)
