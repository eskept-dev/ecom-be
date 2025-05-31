from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from multiselectfield import MultiSelectField

from app.user.helpers import generate_activation_code


class UserRole(models.TextChoices):
    ADMIN = 'admin'
    CUSTOMER = 'customer'
    BUSINESS = 'business'


class UserStatus(models.TextChoices):
    NEW = 'new'
    ACTIVE = 'active'
    WAITING_FOR_APPROVAL = 'waiting_for_approval'
    INACTIVE = 'inactive'
    REJECTED = 'rejected'


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        
        if not password:
            user.set_unusable_password()
        else:
            user.set_password(password)
            
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    first_name = None
    last_name = None
    is_staff = None
    is_active = None
    date_joined = None
    last_login = None
    is_verified = None
    is_superuser = None

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.CUSTOMER)
    status = models.CharField(max_length=20, choices=UserStatus.choices, default=UserStatus.NEW)
    activation_code = models.CharField(default=generate_activation_code, max_length=24, null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'

    objects = UserManager() 

    def __str__(self):
        return self.email

    @property
    def is_customer(self):
        return self.role == UserRole.CUSTOMER

    @property
    def is_business(self):
        return self.role == UserRole.BUSINESS
    
    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    @property
    def is_active(self):
        return self.status == UserStatus.ACTIVE
    
    @property
    def is_inactive(self):
        return self.status == UserStatus.INACTIVE
    
    @property
    def is_new(self):
        return self.status == UserStatus.NEW
    
    @property
    def can_sign_in_by_password(self):
        if self.password is None:
            return False
        return self.is_active and not self.password.startswith('!')

    def activate(self):
        if self.role == UserRole.CUSTOMER:
            self.status = UserStatus.ACTIVE
        else:
            self.status = UserStatus.WAITING_FOR_APPROVAL
        self.activated_at = timezone.now()
        self.activation_code = None
        self.save()

    def deactivate(self):
        self.status = UserStatus.INACTIVE
        self.activation_code = None
        self.save()

    def approve(self):
        self.status = UserStatus.ACTIVE
        self.save()
        
    def reject(self):
        self.status = UserStatus.REJECTED
        self.save()
        
    def renew_activation_code(self):
        self.activation_code = generate_activation_code()
        self.save()


class Gender(models.TextChoices):
    MALE = 'male'
    FEMALE = 'female'
    OTHER = 'other'


class PhoneNumberChannels(models.TextChoices):
    WHATSAPP = 'whatsapp'
    VIBER = 'viber'
    TELEGRAM = 'telegram'


class UserProfile(models.Model):
    avatar_url = models.URLField(null=True, blank=True)
    first_name = models.CharField(max_length=128, null=True, blank=True)
    last_name = models.CharField(max_length=128, null=True, blank=True)
    phone_number = models.CharField(max_length=128, null=True, blank=True)
    available_on = MultiSelectField(choices=PhoneNumberChannels.choices, default=[], null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=8, choices=Gender.choices, null=True, blank=True)
    nationality = models.CharField(max_length=128, null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class BusinessProfile(models.Model):
    name = models.CharField(max_length=128, null=True, blank=True)
    tax_id = models.CharField(max_length=128, null=True, blank=True)
    address = models.CharField(max_length=128, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=128, null=True, blank=True)
    available_on = MultiSelectField(choices=PhoneNumberChannels.choices, default=[], null=True, blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    logo_url = models.URLField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    nationality = models.CharField(max_length=128, null=True, blank=True)
    representative_profile = models.JSONField(default=dict, null=True, blank=True)

    user = models.OneToOneField(User, on_delete=models.CASCADE)
