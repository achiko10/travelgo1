from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.throttling import ScopedRateThrottle
from django.core.cache import cache
from django.utils.crypto import get_random_string
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import stripe
import os
from django.conf import settings

from .serializers import RegisterSerializer, DigitalPassportSerializer, ReferralDashboardSerializer, LeaderboardSerializer
from .models import CustomUser
from .tasks import send_password_reset_email

stripe.api_key = settings.STRIPE_SECRET_KEY


# ─── Auth ──────────────────────────────────────────────────────────────────────

class LoginView(TokenObtainPairView):
    """POST /api/users/login/ — მომხმარებლის ავტორიზაცია"""
    throttle_scope = 'login'


class RegisterView(generics.CreateAPIView):
    """POST /api/users/register/ — ახალი მომხმარებლის რეგისტრაცია + OTP კოდის გაგზავნა"""
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        
        # 4-ნიშნა OTP გენერაცია
        otp_code = get_random_string(length=4, allowed_chars='0123456789')
        cache.set(f'otp_{user.email}', otp_code, timeout=900)  # 15 წუთი
        
        # Resend-ით Gmail-ზე გაგზავნა
        from .tasks import send_otp_email
        try:
            send_otp_email(user.email, otp_code)
        except Exception as e:
            print(f"Error sending OTP to {user.email}: {e}")


class VerifyOTPView(APIView):
    """
    POST /api/users/verify-otp/
    Body: {"email": "user@gmail.com", "code": "1234"}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        code = request.data.get('code')

        if not email or not code:
            return Response({"error": "Email and code are required"}, status=status.HTTP_400_BAD_REQUEST)

        cached_otp = cache.get(f'otp_{email}')
        
        # მივიღოთ როგორც რეალური Resend OTP, ასევე Fallback 1234 სატესტოდ
        is_valid = (cached_otp and str(cached_otp) == str(code)) or (str(code) == "1234")

        if not is_valid:
            return Response({"error": "არასწორი ან ვადაგასული OTP კოდი"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({"error": "მომხმარებელი ვერ მოიძებნა"}, status=status.HTTP_404_NOT_FOUND)

        user.is_active = True
        user.save(update_fields=['is_active'])
        cache.delete(f'otp_{email}')

        refresh = RefreshToken.for_user(user)
        return Response({
            "success": True,
            "message": "ვერიფიკაცია წარმატებულია!",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=status.HTTP_200_OK)


class ResendOTPView(APIView):
    """
    POST /api/users/resend-otp/
    Body: {"email": "user@gmail.com"}
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({"error": "მომხმარებელი ვერ მოიძებნა"}, status=status.HTTP_404_NOT_FOUND)

        otp_code = get_random_string(length=4, allowed_chars='0123456789')
        cache.set(f'otp_{email}', otp_code, timeout=900)

        from .tasks import send_otp_email
        success = send_otp_email(email, otp_code)

        return Response({
            "success": success,
            "message": "ახალი OTP კოდი გაიგზავნა თქვენს Gmail-ზე!"
        }, status=status.HTTP_200_OK)


class SocialLoginView(APIView):
    """POST /api/users/social-login/ — Google OAuth2 ტოკენის ვალიდაცია და JWT გაცემა"""
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'login'

    def post(self, request):
        token = request.data.get('token')
        if settings.DEBUG and token and token.startswith("test_"):
            email = token.replace("test_", "")
            if "@" not in email:
                email = f"{email}@travelgo.com"
            user, created = CustomUser.objects.get_or_create(email=email)
            if created:
                user.username = email.split('@')[0]
                user.save(update_fields=['username'])
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access':  str(refresh.access_token),
                'is_new':  created,
            }, status=status.HTTP_200_OK)

        google_client_id = os.getenv("GOOGLE_CLIENT_ID", "51477845861-vtd3cdi51prn0rm1qn2cqpe54o5aqem1.apps.googleusercontent.com")
        email = None
        full_name = None

        # 1. Try Google ID Token verification (JWT)
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), google_client_id)
            email = idinfo.get('email')
            full_name = idinfo.get('name')
        except Exception:
            # 2. Fallback: Verify as Google OAuth2 Access Token
            try:
                import requests as req
                resp = req.get("https://www.googleapis.com/oauth2/v3/userinfo", headers={"Authorization": f"Bearer {token}"}, timeout=8)
                if resp.status_code == 200:
                    data = resp.json()
                    email = data.get('email')
                    full_name = data.get('name')
                else:
                    t_resp = req.get(f"https://oauth2.googleapis.com/tokeninfo?access_token={token}", timeout=8)
                    if t_resp.status_code == 200:
                        email = t_resp.json().get('email')
            except Exception as net_err:
                return Response({'error': f'Google Auth network verification failed: {str(net_err)}'}, status=status.HTTP_400_BAD_REQUEST)

        if not email:
            return Response({'error': 'Google token is invalid or expired.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user, created = CustomUser.objects.get_or_create(email=email)
            if created:
                user.username = email.split('@')[0]
                user.full_name = full_name or email.split('@')[0]
                user.is_email_verified = True
                user.save(update_fields=['username', 'full_name', 'is_email_verified'])
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access':  str(refresh.access_token),
                'is_new':  created,
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'Google Auth user creation failed: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetRequestView(APIView):
    """POST /api/users/password-reset/ — პაროლის აღდგენის PIN გაგზავნა"""
    permission_classes = [permissions.AllowAny]
    throttle_scope = 'password_reset'

    def post(self, request):
        email = request.data.get('email')
        user  = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({'message': 'If user exists, email was sent.'}, status=status.HTTP_200_OK)
        
        pin  = get_random_string(length=6, allowed_chars='0123456789')
        cache.set(f'pwd_reset_{email}', pin, timeout=1800)
        
        # Direct email send (no Celery needed for local dev)
        from django.core.mail import send_mail
        try:
            send_mail(
                "Travel Go - პაროლის აღდგენა",
                f"პაროლის აღდგენის კოდი: {pin}\nკოდი 30 წუთის განმავლობაში მოქმედებს.",
                'support@travelgo.ge',
                [email],
                fail_silently=True
            )
        except Exception:
            pass
        return Response({'message': 'If user exists, email was sent.'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """POST /api/users/password-reset/confirm/ — პაროლის აღდგენა PIN კოდით"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        pin   = request.data.get('pin')
        new_pwd = request.data.get('new_password')

        cached = cache.get(f'pwd_reset_{email}')
        if not cached or cached != pin:
            return Response({'error': 'Invalid or expired reset PIN'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.filter(email=email).first()
        if not user:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        from django.contrib.auth.password_validation import validate_password
        from django.core.exceptions import ValidationError
        try:
            validate_password(new_pwd, user=user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_pwd)
        user.save()
        cache.delete(f'pwd_reset_{email}')
        return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


# ─── Profile & Leaderboard ─────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/users/profile/ — Digital Passport (პირადი კაბინეტი)"""
    serializer_class   = DigitalPassportSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LeaderboardView(generics.ListAPIView):
    """GET /api/users/leaderboard/ — Top 100 მოგზაური XP-ის მიხედვით. Redis Cache: 5 წუთი"""
    serializer_class   = LeaderboardSerializer
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

from django.db import transaction

class ApplyReferralView(APIView):
    """POST /api/users/referral/apply/ — Referral კოდის გამოყენება. ორივეს +50 Coins +100 XP"""
    permission_classes = [permissions.IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        code = request.data.get('referral_code', '').strip().upper()
        if not code:
            return Response({"error": "კოდი ცარიელია"}, status=status.HTTP_400_BAD_REQUEST)

        # Lock the current user object
        user = CustomUser.objects.select_for_update().get(id=request.user.id)

        if user.referred_by:
            return Response(
                {"error": "თქვენ უკვე გამოიყენეთ რეფერალური კოდი."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.referral_code == code:
            return Response(
                {"error": "საკუთარი კოდის გამოყენება აკრძალულია."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Lock the referring friend object
            friend = CustomUser.objects.select_for_update().get(referral_code=code)
        except CustomUser.DoesNotExist:
            return Response({"error": "არასწორი კოდი."}, status=status.HTTP_400_BAD_REQUEST)

        # ორმხრივი ჯილდო
        user.referred_by  = friend
        user.coins       += 50
        user.xp          += 100
        user.save()

        friend.coins += 50
        friend.xp    += 100
        friend.save()

        return Response({
            "message":       "🎉 +50 Coins and +100 XP awarded to both travelers!",
            "your_new_xp":   user.xp,
            "your_new_coins": user.coins,
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


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    """POST /api/users/payments/webhook/ — Stripe გადახდის დასტურის მიღება (Webhook)"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET', '')

        if webhook_secret:
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
            except ValueError:
                # არასწორი მონაცემები
                return Response({'error': 'Invalid payload'}, status=status.HTTP_400_BAD_REQUEST)
            except stripe.error.SignatureVerificationError:
                # არასწორი ციფრული ხელმოწერა
                return Response({'error': 'Invalid signature'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # თუ საიდუმლო გასაღები არ არის გაწერილი, წაიკითხე პირდაპირ (დეველოპმენტისთვის)
            import json
            try:
                event = json.loads(payload)
            except ValueError:
                return Response({'error': 'Invalid JSON'}, status=status.HTTP_400_BAD_REQUEST)

        # გადახდის წარმატებით დასრულების დამუშავება
        if event.get('type') == 'payment_intent.succeeded':
            payment_intent = event.get('data', {}).get('object', {})
            user_email = payment_intent.get('metadata', {}).get('user_email')
            amount_cents = payment_intent.get('amount') # თანხა ცენტებში

            if user_email and amount_cents:
                from django.db import transaction
                try:
                    with transaction.atomic():
                        # მონაცემების ბლოკირება რბოლის პირობების თავიდან ასაცილებლად
                        user = CustomUser.objects.select_for_update().get(email=user_email)
                        # 1 ცენტი = 1 მონეტა (500 ცენტი = 500 მონეტა)
                        coins_to_add = amount_cents
                        user.coins += coins_to_add
                        user.save()
                except CustomUser.DoesNotExist:
                    pass

        return Response({'success': True}, status=status.HTTP_200_OK)


class UserSearchView(APIView):
    """GET /api/users/search/?q=... — მომხმარებლის ძებნა email ან სახელით"""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        q = request.query_params.get('q', '').strip()
        if len(q) < 2:
            return Response({'results': []})

        from django.db.models import Q
        users = CustomUser.objects.filter(
            Q(email__icontains=q) | Q(full_name__icontains=q)
        ).exclude(id=request.user.id)[:20]

        results = [
            {
                'id': u.id,
                'email': u.email,
                'full_name': u.full_name or u.email.split('@')[0],
                'level': u.level,
                'avatar_skin_color': u.avatar_skin_color,
            }
            for u in users
        ]
        return Response({'results': results})

