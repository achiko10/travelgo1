from django.db import models
from django.conf import settings
from django.utils.crypto import get_random_string


class Category(models.Model):
    # ── ქართული ──────────────────────────────────────────────────────────────
    name = models.CharField(max_length=50, verbose_name="კატეგორია (KA)")
    # ── ინგლისური ─────────────────────────────────────────────────────────────
    name_en = models.CharField(max_length=50, blank=True, verbose_name="Category Name (EN)")
    icon_name = models.CharField(max_length=50, blank=True, help_text="Flutter Icon Name")

    class Meta:
        verbose_name = "კატეგორია"
        verbose_name_plural = "პარტნიორის კატეგორიები"

    def __str__(self):
        return self.name


class Partner(models.Model):
    # ── ქართული ──────────────────────────────────────────────────────────────
    name = models.CharField(max_length=150, verbose_name="პარტნიორის დასახელება (KA)")
    description = models.TextField(verbose_name="შეთავაზების დეტალები (KA)", blank=True)
    terms_and_conditions = models.TextField(verbose_name="წესები და პირობები (KA)", blank=True)

    # ── ინგლისური ─────────────────────────────────────────────────────────────
    name_en = models.CharField(max_length=150, blank=True, verbose_name="Partner Name (EN)")
    description_en = models.TextField(blank=True, verbose_name="Offer Details (EN)")
    terms_and_conditions_en = models.TextField(blank=True, verbose_name="Terms & Conditions (EN)")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='partners')
    logo = models.ImageField(upload_to='partners_logos/', blank=True, null=True)
    location_address = models.CharField(max_length=255, verbose_name="მისამართი (KA)")
    location_address_en = models.CharField(max_length=255, blank=True, verbose_name="Address (EN)")

    latitude = models.FloatField(default=41.7151, db_index=True)
    longitude = models.FloatField(default=44.8271, db_index=True)

    offer_percentage = models.PositiveIntegerField(default=5, verbose_name="ფასდაკლების % (ან ბონუსი)")

    # ── მარკეტინგული / საკონტაქტო ველები ──────────────────────────────────────
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0.0,
                                 verbose_name="შეფასება (0.0-5.0)")
    review_count = models.PositiveIntegerField(default=0, verbose_name="შეფასებების რაოდენობა")
    phone = models.CharField(max_length=30, blank=True, verbose_name="ტელეფონი")
    website = models.URLField(blank=True, verbose_name="ვებსაიტი")
    working_hours = models.CharField(max_length=150, blank=True,
                                     verbose_name="სამუშაო საათები (KA)")
    working_hours_en = models.CharField(max_length=150, blank=True,
                                        verbose_name="Working Hours (EN)")
    price_range = models.CharField(max_length=50, blank=True,
                                   verbose_name="ფასის დიაპაზონი (მაგ: ₾50-₾150)")

    class Meta:
        verbose_name = "პარტნიორი"
        verbose_name_plural = "პარტნიორები"

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class PartnerPhoto(models.Model):
    """პარტნიორის გალერეის ფოტო — ადმინი ამატებს რამდენიც უნდა"""
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE,
                                related_name='photos', verbose_name="პარტნიორი")
    image = models.ImageField(upload_to='partners_photos/', verbose_name="ფოტო")
    caption = models.CharField(max_length=200, blank=True, verbose_name="წარწერა (KA)")
    caption_en = models.CharField(max_length=200, blank=True, verbose_name="Caption (EN)")
    order = models.PositiveIntegerField(default=0, verbose_name="რიგითობა")

    class Meta:
        verbose_name = "პარტნიორის ფოტო"
        verbose_name_plural = "პარტნიორის ფოტოები"
        ordering = ['order', 'id']

    def __str__(self):
        return f"Photo #{self.order} — {self.partner.name}"


class DiscountCoupon(models.Model):
    """
    Discount Coupon — ადმინი ქმნის, Flutter-ი აჩვენებს Check-in-ის შემდეგ.
    task.md Phase 6: 'In-app Currency, Boosts and discount codes'
    """
    STATUS_CHOICES = (
        ('active',  'აქტიური'),
        ('used',    'გამოყენებული'),
        ('expired', 'ვადაგასული'),
    )

    partner = models.ForeignKey(Partner, on_delete=models.CASCADE,
                                related_name='coupons', verbose_name="პარტნიორი")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='coupons', null=True, blank=True,
                             verbose_name="მომხმარებელი (ვისთვის)")
    code = models.CharField(max_length=12, unique=True,
                            verbose_name="კუპონის კოდი", blank=True)
    discount_pct = models.PositiveIntegerField(default=10, verbose_name="ფასდაკლება %")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='active', verbose_name="სტატუსი")
    valid_until = models.DateField(null=True, blank=True, verbose_name="ვარგისიანობის ვადა")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="შექმნის თარიღი")
    used_at = models.DateTimeField(null=True, blank=True, verbose_name="გამოყენების თარიღი")

    class Meta:
        verbose_name = "ფასდაკლების კუპონი"
        verbose_name_plural = "ფასდაკლების კუპონები"
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.code:
            prefix = self.partner.name[:3].upper().replace(' ', '')
            self.code = f"{prefix}-{get_random_string(6, 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789')}"
        super().save(*args, **kwargs)

    def __str__(self):
        user_str = self.user.email if self.user else "ნებისმიერი"
        return f"{self.code} | {self.partner.name} | {self.discount_pct}% | {user_str}"
