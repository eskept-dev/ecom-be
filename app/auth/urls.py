from django.urls import path
from app.auth import views  


urlpatterns = [
    # Sign Up
    path('sign_up', views.SignUpView.as_view(), name='sign_up'),
    path('resend_verification_email', views.ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('activate', views.ActivateUserView.as_view(), name='activate'),
    # Sign In
    path('sign_in', views.SignInView.as_view(), name='sign_in'),
    path('can_sign_in_by_password', views.CanSignInByPasswordView.as_view(), name='can_sign_in_by_password'),
    path('sign_in_by_email', views.SendSignInEmailView.as_view(), name='send_sign_in_email'),
    path('refresh', views.RefreshTokenView.as_view(), name='refresh'),
    # Reset Password
    path('send_reset_password_email', views.SendResetPasswordEmailView.as_view(), name='send_reset_password_email'),
    path('reset_password', views.ResetPasswordView.as_view(), name='reset_password'),
    # Token
    path('pairs_token', views.GetPairsTokenView.as_view(), name='get_pairs_token'),
]
