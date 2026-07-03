from django.db import models

class SystemConfig(models.Model):
    """
    აპლიკაციის გლობალური ცვლადების მართვა (Singleton)
    """
    checkin_radius_meters = models.FloatField(default=40.0, verbose_name="ჩექინის რადიუსი (მეტრებში)")
    referral_bonus_xp = models.PositiveIntegerField(default=100, verbose_name="მოწვევის ბონუსი (XP)")
    referral_bonus_coins = models.PositiveIntegerField(default=50, verbose_name="მოწვევის ბონუსი (Coins)")
    app_maintenance_mode = models.BooleanField(default=False, verbose_name="ტექნიკური შესვენების რეჟიმი")
    min_app_version = models.CharField(max_length=20, default="1.0.0", verbose_name="მინიმალური ვერსია (საჭირო)")

    # ── ორენოვანი ვერსიები ──────────────────────────────────────────────────────
    app_name_ka = models.CharField(max_length=100, default="თრეველგო", verbose_name="აპლიკაციის სახელი (KA)")
    app_name_en = models.CharField(max_length=100, default="TravelGo", verbose_name="App Name (EN)")
    maintenance_message_ka = models.TextField(default="მიმდინარეობს ტექნიკური სამუშაოები", verbose_name="შეტყობინება შესვენებაზე (KA)")
    maintenance_message_en = models.TextField(default="Under maintenance", verbose_name="Maintenance Message (EN)")

    class Meta:
        verbose_name = "აპლიკაციის პარამეტრი"
        verbose_name_plural = "⚙️ აპლიკაციის პარამეტრები (გლობალური)"

    def save(self, *args, **kwargs):
        # უზრუნველყოფს რომ მხოლოდ 1 ჩანაწერი იყოს
        self.pk = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return "გლობალური პარამეტრები"


class OnboardingSlide(models.Model):
    """
    Welcome ეკრანების სლაიდები (დინამიური მართვა)
    """
    title = models.CharField(max_length=150, verbose_name="სათაური (KA)")
    description = models.TextField(verbose_name="აღწერა (KA)")

    title_en = models.CharField(max_length=150, blank=True, verbose_name="Title (EN)")
    description_en = models.TextField(blank=True, verbose_name="Description (EN)")

    image = models.ImageField(upload_to='onboarding/', blank=True, null=True, verbose_name="სლაიდის სურათი")
    step_number = models.PositiveIntegerField(default=1, verbose_name="ნაბიჯი (#)")
    is_active = models.BooleanField(default=True, verbose_name="აქტიურია")

    class Meta:
        verbose_name = "ონბორდინგ სლაიდი"
        verbose_name_plural = "📱 ონბორდინგ სლაიდები"
        ordering = ['step_number']

    def __str__(self):
        return f"ნაბიჯი {self.step_number}: {self.title}"


class AppTranslation(models.Model):
    """
    აპლიკაციის ფრონტენდის ინტერფეისის სტატიკური ტექსტების ორენოვანი ბაზა
    """
    CATEGORY_CHOICES = (
        ('auth', 'ავტორიზაცია (Auth)'),
        ('map', 'რუკა & დეტალები (Map & Details)'),
        ('profile', 'პროფილი & ინვენტარი (Profile & Backpack)'),
        ('store', 'მაღაზია & პარტნიორები (Store & Coupons)'),
        ('ai', 'AI დაგეგმარება (AI Planner)'),
        ('errors', 'შეცდომები & ვალიდაცია (Errors & Val)'),
    )

    key = models.CharField(max_length=100, unique=True, verbose_name="ტექსტის იდენტიფიკატორი (Key)")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='map', verbose_name="კატეგორია")
    text_ka = models.TextField(verbose_name="ქართული ტექსტი (KA)")
    text_en = models.TextField(verbose_name="ინგლისური ტექსტი (EN)")

    class Meta:
        verbose_name = "ინტერფეისის თარგმანი"
        verbose_name_plural = "🆎 ინტერფეისის თარგმანები (Localization)"
        ordering = ['category', 'key']

    def __str__(self):
        return f"{self.category} | {self.key}"


class ARTutorialStep(models.Model):
    """
    AR ტუტორიალის ნაბიჯ-ნაბიჯ მართვის მოდელი
    """
    ACTION_CHOICES = (
        ('look_around', 'ტელეფონის ტრიალი (Look Around)'),
        ('tap_poi', 'ობიექტზე კლიკი (Tap POI)'),
        ('checkin', 'ჩექინის დასრულება (Checkin)'),
    )

    step_number = models.PositiveIntegerField(default=1, verbose_name="ნაბიჯი (#)")
    target_action = models.CharField(max_length=30, choices=ACTION_CHOICES, default='look_around', verbose_name="სამიზნე მოქმედება")
    
    instruction_ka = models.TextField(verbose_name="ინსტრუქცია (KA)")
    instruction_en = models.TextField(verbose_name="Instruction (EN)", blank=True)
    
    lottie_animation_name = models.CharField(
        max_length=100, 
        blank=True, 
        verbose_name="Lottie ანიმაცია",
        help_text="მაგ: scan_device, success_confetti"
    )
    is_active = models.BooleanField(default=True, verbose_name="აქტიურია")

    class Meta:
        verbose_name = "AR ტუტორიალის ნაბიჯი"
        verbose_name_plural = "🕶️ AR ტუტორიალის ნაბიჯები"
        ordering = ['step_number']

    def __str__(self):
        return f"AR ნაბიჯი {self.step_number}: {self.get_target_action_display()}"
