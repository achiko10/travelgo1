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
        db_index=True,
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
    is_claimed = models.BooleanField(default=False, verbose_name="პრიზი აღებულია")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'quest'], name='unique_user_quest_progress')
        ]
        verbose_name = "ქვესთის პროგრესი"

    def __str__(self):
        return f"{self.user.email} -> {self.quest.title}"


class QuizQuestion(models.Model):
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE, related_name='quiz_questions', verbose_name="საინტერესო წერტილი (POI)")
    question = models.CharField(max_length=255, verbose_name="კითხვა (KA)")
    question_en = models.CharField(max_length=255, blank=True, verbose_name="Question (EN)")
    
    # 4 Answers
    answer1 = models.CharField(max_length=150, verbose_name="პასუხი 1 (KA)")
    answer1_en = models.CharField(max_length=150, blank=True, verbose_name="Answer 1 (EN)")
    
    answer2 = models.CharField(max_length=150, verbose_name="პასუხი 2 (KA)")
    answer2_en = models.CharField(max_length=150, blank=True, verbose_name="Answer 2 (EN)")
    
    answer3 = models.CharField(max_length=150, verbose_name="პასუხი 3 (KA)")
    answer3_en = models.CharField(max_length=150, blank=True, verbose_name="Answer 3 (EN)")
    
    answer4 = models.CharField(max_length=150, verbose_name="პასუხი 4 (KA)")
    answer4_en = models.CharField(max_length=150, blank=True, verbose_name="Answer 4 (EN)")
    
    correct_index = models.PositiveIntegerField(default=0, help_text="0-დან 3-მდე (რომელი პასუხია სწორი)")

    class Meta:
        verbose_name = "ქვიზის კითხვა"
        verbose_name_plural = "ქვიზის კითხვები"

    def __str__(self):
        return f"{self.poi.name} -> {self.question}"


class UserQuizSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE)
    score = models.PositiveIntegerField(default=0)
    date_submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "ქვიზის შედეგი"
        verbose_name_plural = "ქვიზების შედეგები"


class UserPuzzleSubmission(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    poi = models.ForeignKey(PointOfInterest, on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "პაზლის შედეგი"
        verbose_name_plural = "პაზლების შედეგები"

