from django.db import models

from app.base.models import BaseModel


class SupplierStatus(models.TextChoices):
    NEW = 'new'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    INACTIVE = 'inactive'


class Supplier(BaseModel):
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20, choices=SupplierStatus.choices, default=SupplierStatus.APPROVED)
    description = models.TextField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    tax_id = models.CharField(max_length=128, null=True, blank=True)

    contact_profile = models.JSONField(default=dict, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=128, null=True, blank=True, unique=True)
    contact_email = models.EmailField(null=True, blank=True, unique=True)
    website = models.URLField(null=True, blank=True, unique=True)
    logo_url = models.URLField(null=True, blank=True)
    nationality = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def is_active(self):
        return self.status == SupplierStatus.APPROVED

    def approve(self):
        self.status = SupplierStatus.APPROVED
        self.save()

    def reject(self):
        self.status = SupplierStatus.REJECTED
        self.save()

    def deactivate(self):
        self.status = SupplierStatus.INACTIVE
        self.save()
