
from django.urls import path

from app.file import views

urlpatterns = [
    path('upload', views.FileUploadView.as_view(), name='file-upload'),
    path('delete', views.FileDeleteView.as_view(), name='file-delete'),
]
