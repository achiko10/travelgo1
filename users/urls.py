from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    RegisterView, VerifyOTPView, ResendOTPView, ProfileView, LeaderboardView,
    ApplyReferralView, MyReferralDashboardView,
    SocialLoginView, PasswordResetRequestView,
    PasswordResetConfirmView, CreatePaymentIntentView,
    StripeWebhookView, LoginView, UserSearchView
)

urlpatterns = [
    # Auth endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('resend-otp/', ResendOTPView.as_view(), name='resend_otp'),
    path('login/', LoginView.as_view(), name='token_obtain_pair'), # Email and Password login
    path('social-login/', SocialLoginView.as_view(), name='social_login'),
    path('payments/create-intent/', CreatePaymentIntentView.as_view(), name='create_payment'),
    path('payments/webhook/', StripeWebhookView.as_view(), name='stripe_webhook'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # Auto-login refresh token
    
    # Profile & Leaderboard
    path('profile/', ProfileView.as_view(), name='profile'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('referral/apply/',        ApplyReferralView.as_view(),          name='apply_referral'),
    path('referral/my-dashboard/', MyReferralDashboardView.as_view(),    name='referral_dashboard'),
    path('search/',                UserSearchView.as_view(),             name='user_search'),

]

