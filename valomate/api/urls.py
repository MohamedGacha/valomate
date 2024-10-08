from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import ChangePasswordView, ChangeUsernameView, CustomTokenObtainPairView, DeleteAccountView, ForgotPasswordView, PasswordResetConfirmView, ResendVerificationEmailView, UserRegisterView, VerifyEmailView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify_email'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('resend-verification-email/', ResendVerificationEmailView.as_view(), name='resend_verification_email'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('change-username/', ChangeUsernameView.as_view(), name='change-username'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('delete-account/', DeleteAccountView.as_view(), name='delete-account'),

    path('valorant/', include('valorantProfile.urls')),
]
