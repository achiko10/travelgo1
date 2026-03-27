from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, ProfileView, LeaderboardView, ApplyReferralView, SocialLoginView, PasswordResetRequestView, PasswordResetConfirmView, CreatePaymentIntentView

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'), # Email and Password login
    path('social-login/', SocialLoginView.as_view(), name='social_login'),
    path('payments/create-intent/', CreatePaymentIntentView.as_view(), name='create_payment'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # Auto-login refresh token
    
    # Profile & Leaderboard
    path('profile/', ProfileView.as_view(), name='profile'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('referral/apply/', ApplyReferralView.as_view(), name='apply_referral'),
]
