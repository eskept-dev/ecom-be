from django.db import models
from django.forms import ValidationError

from app.base.models import BaseModel, SoftDeleteMixin


class ArticlePage(models.TextChoices):
    HOME = "home"
    BOOKING_CONFIRMATION = "booking_confirmation"
    PRODUCT_LIST = "product_list"
    PAYMENT = "payment"


class ArticleStatus(models.TextChoices):
    DRAFT = "draft"
    PUBLISHED = "published"
    UNPUBLISHED = "unpublished"


class Article(BaseModel, SoftDeleteMixin):

    title_vi = models.CharField(max_length=255, null=True, blank=True)
    title_en = models.CharField(max_length=255, null=True, blank=True)
    content_vi = models.TextField(null=True, blank=True)
    content_en = models.TextField(null=True, blank=True)
    
    thumbnail_url = models.URLField(null=True, blank=True)
    cover_url = models.URLField(null=True, blank=True)

    slug = models.SlugField(max_length=255, unique=True)
    status = models.CharField(max_length=32, choices=ArticleStatus.choices, default=ArticleStatus.DRAFT)

    pages = models.JSONField(default=list)
    tags = models.JSONField(default=list)
    product_ids = models.JSONField(default=list)

    def __str__(self):
        return self.title_vi or self.title_en
    
    def validate(self):
        self.validate_title()
        self.validate_content()
        self.validate_pages()
    
    def validate_title(self):
        if not self.title_vi and not self.title_en:
            raise ValidationError("Title is required")
    
    def validate_content(self):
        if not self.content_vi and not self.content_en:
            raise ValidationError("Content is required")

    def validate_pages(self):
        if self.pages:
            for page in self.pages:
                if page not in ArticlePage.values:
                    raise ValidationError(f"Invalid page: {page}")
                
    def publish(self):
        self.status = ArticleStatus.PUBLISHED
        self.save()

    def unpublish(self):
        self.status = ArticleStatus.UNPUBLISHED
        self.save()
