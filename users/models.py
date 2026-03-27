from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('username', email.split('@')[0])
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        
        # Auto-generate a secure 6 digit referral code for each new user
        from django.utils.crypto import get_random_string
        user.referral_code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
        
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    # Core Auth fields
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True, unique=True, verbose_name="ტელეფონის ნომერი")
    
    # Profile fields (as requested in MVP)
    full_name = models.CharField(max_length=255, blank=True, verbose_name="სრული სახელი")
    profile_picture = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="პროფილის სურათი")
    country = models.CharField(max_length=100, blank=True, verbose_name="ქვეყანა")
    city = models.CharField(max_length=100, blank=True, verbose_name="ქალაქი")
    preferred_language = models.CharField(max_length=10, default='en')
    
    # Traveler Info
    TRAVELER_TYPES = (
        ('solo', 'მარტო (Solo)'),
        ('couple', 'წყვილი (Couple)'),
        ('group', 'ჯგუფი (Group)'),
    )
    traveler_type = models.CharField(max_length=20, choices=TRAVELER_TYPES, blank=True)
    
    # Phase 5: Avatar System (Visual Customization)
    avatar_skin_color = models.CharField(max_length=20, default="#FFDCB2", verbose_name="კანის ფერი (Hex)")
    avatar_hair_style = models.CharField(max_length=50, default="short_black", verbose_name="თმის სტილი")
    avatar_clothing = models.CharField(max_length=50, default="basic_tshirt", verbose_name="ტანსაცმელი")

    # Interests stored simply
    interests = models.TextField(blank=True, help_text="მაგ: culture, food, nightlife, adventure")
    
    # Gamification basics (Reward System)
    xp = models.PositiveIntegerField(default=0, verbose_name="XP ქულები")
    level = models.PositiveIntegerField(default=1, verbose_name="დონე (Level)")
    coins = models.PositiveIntegerField(default=0, verbose_name="შიდა ვალუტა (Coins)")

    # Phase 7: Referral System
    referral_code = models.CharField(max_length=6, unique=True, blank=True, null=True, verbose_name="უნიკალური კოდი")
    referred_by = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='invited_users', verbose_name="ვინ მოიწვია")

    # Disable username login requirement, use email instead
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email} (Lvl: {self.level})"

class AnalyticsProxy(CustomUser):
    """ Proxy Model specifically for Phase 8 Admin Analytics Dashboard """
    class Meta:
        proxy = True
        verbose_name = "მოგზაური (სტატისტიკა)"
        verbose_name_plural = "პლატფორმის ანალიტიკა (Dashboard)"
