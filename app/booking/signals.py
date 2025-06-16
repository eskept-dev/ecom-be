from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from app.core.utils.logger import logger

from app.booking.models import BookingItem
