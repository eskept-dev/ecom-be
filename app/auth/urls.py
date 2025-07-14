from django.urls import path, include

from app.auth import views  

urlpatterns = [
    # Sign Up
    path('auth/sign_up', views.SignUpView.as_view(), name='sign_up'),
    path('auth/resend_verification_email', views.ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('auth/activate', views.ActivateUserView.as_view(), name='activate'),
    # Sign In
    path('auth/sign_in', views.SignInView.as_view(), name='sign_in'),
    path('auth/can_sign_in_by_password', views.CanSignInByPasswordView.as_view(), name='can_sign_in_by_password'),
    path('auth/sign_in_by_email', views.SendSignInEmailView.as_view(), name='send_sign_in_email'),
    path('auth/refresh', views.RefreshTokenView.as_view(), name='refresh'),
    # Reset Password
    path('auth/send_reset_password_email', views.SendResetPasswordEmailView.as_view(), name='send_reset_password_email'),
    path('auth/reset_password', views.ResetPasswordAPIView.as_view(), name='reset_password'),
    # Token
    path('auth/pairs_token', views.GetPairsTokenView.as_view(), name='get_pairs_token'),

    # Admin
    path('auth/admin/sign_in', views.AdminSignInView.as_view(), name='admin_sign_in'),
    path('auth/admin/internal_user', views.AdminCreateInternalUserView.as_view(), name='admin_create_internal_user'),
    path('auth/admin/activate_user', views.AdminActivateUserView.as_view(), name='admin_activate_user'),
    path('auth/admin/reset_password', views.AdminResetPasswordAPIView.as_view(), name='admin_reset_password'),
]
