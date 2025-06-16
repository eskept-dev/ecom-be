from django.db import models

from app.base.models import BaseModel
from app.booking.models import Booking


PERSONAL_INFORMATION_REQUIRED_FIELDS = [
    "first_name",
    "last_name",
    "date_of_birth",
    "gender",
    "nationality",
    "email",
    "place_of_birth",
    "have_you_visited_vietnam_before",
    "do_you_have_multiple_nationalities",
]
CONTACT_INFORMATION_REQUIRED_FIELDS = [
    'permanent_residential_address',
    'contact_address',
    'phone_number',
    'emergency_contact_full_name',
    'emergency_contact_current_residential_address',
    'emergency_contact_phone_number',
    'emergency_contact_relationship',
]
TRIP_INFORMATION_REQUIRED_FIELDS = [
    'purpose_of_entry',
    'intended_date_of_entry',
    'intended_length_of_stay',
    'resident_in_vietnam',
    'province',
    'city',
    'district',
    'ward',
    'intended_border_gate_of_entry',
    'intended_border_gate_of_exit',
]
REQUESTED_INFORMATION_REQUIRED_FIELDS = [
    'to_issue_visa_for',
    'grant_visa_valid_from',
    'passport_number',
    'type_of_visa',
    'date_of_issue',
    'expiry_date',
]


class EVisaApplicationStatus(models.TextChoices):
    NEW = "new"
    PROCESSING = "processing"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EVisaApplication(BaseModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=EVisaApplicationStatus.choices, default=EVisaApplicationStatus.NEW)
    note = models.TextField(null=True, blank=True)
    
    total_applicants = models.IntegerField(default=1)
    total_completed_applicants = models.IntegerField(default=0)
    total_incomplete_applicants = models.IntegerField(default=0)


class EVisaApplicantStatus(models.TextChoices):
    NEW = "new"
    PROCESSING = "processing"
    REQUEST_TO_UPDATE = "request_to_update"
    SUBMITTED = "submitted"
    PROCESSING_BY_GOVERNMENT = "processing_by_government"
    REJECTED_BY_GOVERNMENT = "rejected_by_government"
    REQUEST_TO_UPDATE_BY_GOVERNMENT = "request_to_update_by_government"
    APPROVED_BY_GOVERNMENT = "approved_by_government"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class EVisaApplicant(BaseModel):
    application = models.ForeignKey(EVisaApplication, on_delete=models.CASCADE)
    status = models.CharField(max_length=32, choices=EVisaApplicationStatus.choices, default=EVisaApplicationStatus.NEW)

    data = models.JSONField()
    evisa_truth_acknowledgement_and_fee_policy_agreement = models.BooleanField(default=False)
    passport_image_url = models.URLField(null=True, blank=True)
    portrait_image_url = models.URLField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.validate_data():
            raise ValueError("Invalid data")
        super().save(*args, **kwargs)

    def validate_data(self):
        personal_information = self.personal_information
        if not self.validate_visa_section(personal_information, PERSONAL_INFORMATION_REQUIRED_FIELDS):
            return False

        contact_information = self.contact_information
        if not self.validate_visa_section(contact_information, CONTACT_INFORMATION_REQUIRED_FIELDS):
            return False

        requested_information = self.requested_information
        if not self.validate_visa_section(requested_information, REQUESTED_INFORMATION_REQUIRED_FIELDS):
            return False

        trip_information = self.trip_information
        if not self.validate_visa_section(trip_information, TRIP_INFORMATION_REQUIRED_FIELDS):
            return False

        return True

    def validate_visa_section(self, data, required_fields):
        for field in required_fields:
            if field not in data:
                return False
        return True
