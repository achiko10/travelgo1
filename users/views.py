from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.cache import cache
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import stripe
import os
from django.conf import settings

from .serializers import RegisterSerializer, DigitalPassportSerializer, ReferralDashboardSerializer
from .models import CustomUser
from .tasks import send_password_reset_email

stripe.api_key = settings.STRIPE_SECRET_KEY


# ─── Auth ──────────────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/ — ახალი მომხმარებლის რეგისტრაცია"""
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class SocialLoginView(APIView):
    """POST /api/users/social-login/ — Google OAuth2 ტოკენის ვალიდაცია და JWT გაცემა"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "YOUR_GOOGLE_CLIENT_ID")
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
            email = idinfo['email']
            user, created = CustomUser.objects.get_or_create(email=email)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access':  str(refresh.access_token),
                'is_new':  created,
            }, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'error': 'Invalid Google Token'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """POST /api/users/password-reset/ — პაროლის აღდგენის PIN გაგზავნა Celery-ით"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        user  = CustomUser.objects.filter(email=email).first()
        if user:
            pin = get_random_string(length=6, allowed_chars='0123456789')
            cache.set(f'pwd_reset_{email}', pin, timeout=600)
            send_password_reset_email.delay(email, pin)
        return Response({"message": "თუ მეილი არსებობს სისტემაში, 6 ნიშნა კოდი გაიგზავნა."})


class PasswordResetConfirmView(APIView):
    """POST /api/users/password-reset/confirm/ — PIN-ის დადასტურება და პაროლის შეცვლა"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email        = request.data.get('email')
        pin          = request.data.get('pin')
        new_password = request.data.get('new_password')

        valid_pin = cache.get(f'pwd_reset_{email}')
        if valid_pin and valid_pin == pin:
            user = CustomUser.objects.filter(email=email).first()
            if user and new_password:
                user.set_password(new_password)
                user.save()
                cache.delete(f'pwd_reset_{email}')
                return Response({"message": "პაროლი წარმატებით შეიცვალა!"})
        return Response(
            {"error": "PIN კოდი არასწორია ან ვადა გაუვიდა."},
            status=status.HTTP_400_BAD_REQUEST
        )


# ─── Profile & Leaderboard ─────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/profile/ — Digital Passport (პირადი კაბინეტი)"""
    serializer_class   = DigitalPassportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LeaderboardView(generics.ListAPIView):
    """GET /api/users/leaderboard/ — Top 100 მოგზაური XP-ის მიხედვით. Redis Cache: 5 წუთი"""
    serializer_class   = DigitalPassportSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        cached_ids = cache.get('global_leaderboard')
        if cached_ids is not None:
            users = CustomUser.objects.filter(id__in=cached_ids).order_by('-xp')
            if users.exists():
                return users

        qs       = CustomUser.objects.filter(is_active=True).order_by('-xp')[:100]
        user_ids = list(qs.values_list('id', flat=True))
        cache.set('global_leaderboard', user_ids, timeout=300)
        return qs


# ─── Referral ──────────────────────────────────────────────────────────────────

class ApplyReferralView(APIView):
    """POST /api/users/referral/apply/ — Referral კოდის გამოყენება. ორივეს +50 Coins +100 XP"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('referral_code', '').strip().upper()
        if not code:
            return Response({"error": "კოდი ცარიელია"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.referred_by:
            return Response(
                {"error": "თქვენ უკვე გამოიყენეთ რეფერალური კოდი."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.user.referral_code == code:
            return Response(
                {"error": "საკუთარი კოდის გამოყენება აკრძალულია."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            friend = CustomUser.objects.get(referral_code=code)
        except CustomUser.DoesNotExist:
            return Response({"error": "არასწორი კოდი."}, status=status.HTTP_400_BAD_REQUEST)

        # ორმხრივი ჯილდო
        request.user.referred_by  = friend
        request.user.coins       += 50
        request.user.xp          += 100
        request.user.save()

        friend.coins += 50
        friend.xp    += 100
        friend.save()

        return Response({
            "message":       "🎉 +50 Coins and +100 XP awarded to both travelers!",
            "your_new_xp":   request.user.xp,
            "your_new_coins": request.user.coins,
        }, status=status.HTTP_200_OK)


class MyReferralDashboardView(APIView):
    """
    GET /api/users/referral/my-dashboard/
    მომხმარებლის რეფერალური Dashboard:
    - საკუთარი კოდი
    - მოწვეული მეგობრები (სახელი, თარიღი)
    - სულ გამომუშავებული XP referral-ებიდან
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user         = request.user
        invited      = user.invited_users.all()
        total_earned = invited.count() * 100  # 100 XP per referral

        friends_data = [
            {
                "email":      f.email,
                "full_name":  f.full_name or f.email.split('@')[0],
                "level":      f.level,
                "joined":     f.date_joined.strftime('%Y-%m-%d'),
            }
            for f in invited
        ]

        return Response({
            "your_referral_code":       user.referral_code,
            "total_friends_invited":    invited.count(),
            "total_xp_earned_referral": total_earned,
            "friends":                  friends_data,
        })


# ─── Payments ──────────────────────────────────────────────────────────────────

class CreatePaymentIntentView(APIView):
    """POST /api/users/payments/create-intent/ — Stripe Payment Intent (შიდა ვალუტის შეძენა)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        amount = request.data.get('amount', 500)  # 500 cents = $5.00
        try:
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='usd',
                metadata={'user_email': request.user.email}
            )
            return Response({'client_secret': intent.client_secret})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

