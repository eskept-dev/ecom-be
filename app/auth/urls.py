from django.urls import path
from app.auth import views  

urlpatterns = [
    path('sign_up', views.SignUpView.as_view(), name='sign_up'),
    path('resend_verification_email', views.ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('activate', views.ActivateUserView.as_view(), name='activate'),
    path('sign_in', views.SignInView.as_view(), name='sign_in'),
    path('send_sign_in_email', views.SendSignInEmailView.as_view(), name='send_sign_in_email'),
    path('refresh', views.RefreshTokenView.as_view(), name='refresh'),
]