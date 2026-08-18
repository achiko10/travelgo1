from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Use email prefix + unique suffix for username to prevent duplicate username collisions
        import uuid
        username_prefix = email.split('@')[0]
        unique_suffix = uuid.uuid4().hex[:6]
        extra_fields.setdefault('username', f"{username_prefix}_{unique_suffix}")
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
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

    def calculate_level(self):
        """ექსპონენციალური XP სისტემა: RequiredXP = Level^1.5 * 100"""
        import math
        current_level = 1
        accumulated_xp = 0
        while True:
            needed = int((current_level ** 1.5) * 100)
            if self.xp < accumulated_xp + needed:
                break
            accumulated_xp += needed
            current_level += 1
        return current_level

    def xp_for_next_level(self):
        return int((self.level ** 1.5) * 100)

    def __str__(self):
        return f"{self.email} (Lvl: {self.level})"

class AnalyticsProxy(CustomUser):
    """ Proxy Model specifically for Phase 8 Admin Analytics Dashboard """
    class Meta:
        proxy = True
        verbose_name = "მოგზაური (სტატისტიკა)"
        verbose_name_plural = "პლატფორმის ანალიტიკა (Dashboard)"


from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

@receiver(pre_save, sender=CustomUser)
def generate_user_referral_code(sender, instance, **kwargs):
    if not instance.referral_code:
        unique = False
        while not unique:
            code = get_random_string(length=6, allowed_chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
            # Query the database to check if the code already exists
            if not sender.objects.filter(referral_code=code).exists():
                instance.referral_code = code
                unique = True



