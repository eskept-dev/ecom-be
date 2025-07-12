
from django.urls import path

from app.file import views

urlpatterns = [
    path('file/upload', views.FileUploadView.as_view(), name='file-upload'),
    path('file/delete', views.FileDeleteView.as_view(), name='file-delete'),
]
