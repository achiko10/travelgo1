from django.db import models
from django.conf import settings

class Badge(models.Model):
    RARITY_CHOICES = (
        ('common', 'Common'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    )
    # ── ქართული ──────────────────────────────────────────────────────────────
    name = models.CharField(max_length=150, verbose_name="დასახელება (KA)")
    description = models.TextField(verbose_name="აღწერა (KA)")

    # ── ინგლისური ─────────────────────────────────────────────────────────────
    name_en = models.CharField(max_length=150, blank=True, verbose_name="Name (EN)")
    description_en = models.TextField(blank=True, verbose_name="Description (EN)")

    image = models.ImageField(upload_to='badges/', null=True, blank=True)
    rarity = models.CharField(max_length=50, choices=RARITY_CHOICES, default='common')

    # ── მაღაზიის ველები ───────────────────────────────────────────────────────
    coin_price = models.PositiveIntegerField(default=0, verbose_name="ფასი მონეტებში")
    is_for_sale = models.BooleanField(default=False, verbose_name="იყიდება მაღაზიაში")

    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"


class Skin(models.Model):
    # ── ქართული ──────────────────────────────────────────────────────────────
    name = models.CharField(max_length=150, verbose_name="სკინის სახელი (KA)")
    description = models.TextField(verbose_name="აღწერა (KA)")
    region_unlock = models.CharField(max_length=100, blank=True,
                                     verbose_name="განბლოკვის რეგიონი (KA)",
                                     help_text="მაგ: აჭარა, სვანეთი")

    # ── ინგლისური ─────────────────────────────────────────────────────────────
    name_en = models.CharField(max_length=150, blank=True, verbose_name="Skin Name (EN)")
    description_en = models.TextField(blank=True, verbose_name="Description (EN)")
    region_unlock_en = models.CharField(max_length=100, blank=True,
                                        verbose_name="Unlock Region (EN)",
                                        help_text="e.g. Adjara, Svaneti")

    image = models.ImageField(upload_to='skins/', null=True, blank=True)

    # ── მაღაზიის ველები ───────────────────────────────────────────────────────
    coin_price = models.PositiveIntegerField(default=0, verbose_name="ფასი მონეტებში")
    is_for_sale = models.BooleanField(default=False, verbose_name="იყიდება მაღაზიაში")

    def __str__(self):
        return self.name


class UserInventory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inventory')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE, null=True, blank=True)
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE, null=True, blank=True)
    date_unlocked = models.DateTimeField(auto_now_add=True)
    location_unlocked_from = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            # ან badge, ან skin — ზუსტად ერთ-ერთი უნდა იყოს შევსებული
            models.CheckConstraint(
                condition=(
                    models.Q(badge__isnull=False, skin__isnull=True) |
                    models.Q(badge__isnull=True, skin__isnull=False)
                ),
                name='inventory_badge_xor_skin'
            ),
            # მომხმარებელს ერთი badge მხოლოდ ერთხელ შეიძლება ჰქონდეს
            models.UniqueConstraint(
                fields=['user', 'badge'],
                condition=models.Q(badge__isnull=False),
                name='unique_user_badge'
            ),
            # მომხმარებელს ერთი skin მხოლოდ ერთხელ შეიძლება ჰქონდეს
            models.UniqueConstraint(
                fields=['user', 'skin'],
                condition=models.Q(skin__isnull=False),
                name='unique_user_skin'
            ),
        ]
        verbose_name = "ინვენტარი"

    def __str__(self):
        item = self.badge.name if self.badge else (self.skin.name if self.skin else "Item")
        return f"{self.user.email} -> {item}"
