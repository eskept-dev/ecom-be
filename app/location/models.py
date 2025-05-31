from django.db import models

from app.base.models import BaseModel


class LocationType(models.TextChoices):
    AIRPORT = 'airport'
    HOTEL = 'hotel'
    OTHER = 'other'


class Location(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    type = models.CharField(max_length=255, choices=LocationType.choices)
    order = models.IntegerField(default=0)
    is_enabled = models.BooleanField(default=True)
    
    address = models.CharField(max_length=255)
    province = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    district = models.CharField(max_length=255)
    ward = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name
