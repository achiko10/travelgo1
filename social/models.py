from django.db import models
from django.conf import settings


class Friendship(models.Model):
    """
    მომხმარებლებს შორის მეგობრობის კავშირი.
    from_user -> to_user, status: pending / accepted / blocked
    """
    STATUS_CHOICES = (
        ('pending',  'მოლოდინში'),
        ('accepted', 'დადასტურებული'),
        ('blocked',  'დაბლოკილი'),
    )

    from_user  = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_friend_requests',
        verbose_name="გამომგზავნი"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_friend_requests',
        verbose_name="მიმღები"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="სტატუსი"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="შექმნის თარიღი")

    class Meta:
        unique_together = ('from_user', 'to_user')
        verbose_name = "მეგობრობა"
        verbose_name_plural = "🤝 მეგობრები"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.email} -> {self.to_user.email} [{self.status}]"


class FriendActivity(models.Model):
    """
    სოციალური არხი (Social Feed) — მეგობრების ქმედებები
    """
    ACTIVITY_TYPE_CHOICES = (
        ('checkin',          '📍 ჩექინი'),
        ('level_up',         '⬆️ დონის ამაღლება'),
        ('badge_earned',     '🏅 ბეჯის მიღება'),
        ('quest_completed',  '✅ ქვესთის დასრულება'),
        ('skin_unlocked',    '🎨 სკინის განბლოკვა'),
        ('joined',           '🎉 შეუერთდა TravelGo-ს'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name="მომხმარებელი"
    )
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPE_CHOICES,
        verbose_name="ქმედების ტიპი"
    )
    # ოფციური ForeignKey-ები, დამოკიდებულია ქმედებაზე
    poi = models.ForeignKey(
        'maps.PointOfInterest',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="ლოკაცია (ჩექინისთვის)"
    )
    badge = models.ForeignKey(
        'inventory.Badge',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="ბეჯი (badge_earned-ისთვის)"
    )
    skin = models.ForeignKey(
        'inventory.Skin',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name="სკინი (skin_unlocked-ისთვის)"
    )
    xp_earned = models.PositiveIntegerField(default=0, verbose_name="მიღებული XP")
    new_level  = models.PositiveIntegerField(null=True, blank=True, verbose_name="ახალი დონე (level_up-ისთვის)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="თარიღი")

    class Meta:
        verbose_name = "სოციალური ქმედება"
        verbose_name_plural = "📰 სოციალური არხი (Feed)"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} | {self.get_activity_type_display()} | {self.created_at.strftime('%d %b %Y')}"


class ChallengeInvite(models.Model):
    """
    მეგობრის გამოწვევა კონკრეტულ ლოკაციაზე ჩასასვლელად
    """
    STATUS_CHOICES = (
        ('pending',   '⏳ მოლოდინში'),
        ('accepted',  '✅ მიღებულია'),
        ('declined',  '❌ უარყოფილია'),
        ('completed', '🏆 დასრულებულია'),
        ('expired',   '🕐 ვადაგასულია'),
    )

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_challenges',
        verbose_name="გამომგზავნი"
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_challenges',
        verbose_name="მიმღები"
    )
    poi = models.ForeignKey(
        'maps.PointOfInterest',
        on_delete=models.CASCADE,
        verbose_name="სამიზნე ლოკაცია"
    )
    message = models.TextField(
        blank=True,
        verbose_name="პირადი შეტყობინება"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="სტატუსი"
    )
    bonus_xp = models.PositiveIntegerField(
        default=25,
        verbose_name="ბონუს XP (გამარჯვებისთვის)"
    )
    created_at  = models.DateTimeField(auto_now_add=True, verbose_name="შექმნის თარიღი")
    expires_at  = models.DateTimeField(null=True, blank=True, verbose_name="ვადის გასვლის თარიღი")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="დასრულების თარიღი")

    class Meta:
        verbose_name = "გამოწვევა"
        verbose_name_plural = "⚔️ მეგობრების გამოწვევები"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.from_user.email} -> {self.to_user.email} @ {self.poi.name} [{self.status}]"
