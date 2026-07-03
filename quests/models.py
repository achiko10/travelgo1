from django.db import models
from django.conf import settings
from maps.models import PointOfInterest

class DailyQuest(models.Model):
    # ── ქართული ──────────────────────────────────────────────────────────────
    title = models.CharField(max_length=200, verbose_name="ქვესთის სახელი (KA)")
    description = models.TextField(verbose_name="აღწერა (KA)")

    # ── ინგლისური ─────────────────────────────────────────────────────────────
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Quest Title (EN)")
    description_en = models.TextField(blank=True, verbose_name="Description (EN)")

    reward_xp = models.PositiveIntegerField(default=100, verbose_name="პრიზი (XP)")
    reward_coins = models.PositiveIntegerField(default=50, verbose_name="პრიზი (Coins)")
    target_poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE,
                                   null=True, blank=True, verbose_name="სამიზნე ლოკაცია")
    required_checkins = models.PositiveIntegerField(default=1, verbose_name="საჭირო CheckIn-ების რ-ობა")
    date_active = models.DateField(
        default=None,
        null=True,
        blank=True,
        verbose_name="ქვესთის თარიღი",
        help_text="დატოვეთ სადაც, რომლიც ქვესთი აქტიურია იქნება"
    )

    def __str__(self):
        return f"{self.title} ({self.date_active})"


class UserQuestProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quests')
    quest = models.ForeignKey(DailyQuest, on_delete=models.CASCADE)
    progress = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} -> {self.quest.title}"
