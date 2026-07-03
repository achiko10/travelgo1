from django.db import models
from django.conf import settings

class Sprint(models.Model):
    """
    სამუშაო ეტაპები და ვადები (მაგ. Q2 2025 MVP, Batumi Expansion 2026)
    """
    title = models.CharField(max_length=150, verbose_name="ეტაპის დასახელება")
    description = models.TextField(verbose_name="აღწერა (მიზნები)", blank=True)
    start_date = models.DateField(verbose_name="დაწყების თარიღი")
    end_date = models.DateField(verbose_name="დასრულების თარიღი")
    is_completed = models.BooleanField(default=False, verbose_name="დასრულებულია")

    class Meta:
        verbose_name = "ეტაპი (Sprint)"
        verbose_name_plural = "📅 ეტაპები და ვადები (Sprints & Roadmap)"
        ordering = ['start_date']

    def __str__(self):
        status = "✅" if self.is_completed else "⏳"
        return f"{status} {self.title} ({self.start_date} - {self.end_date})"


class ProjectTask(models.Model):
    """
    გუნდის დავალებები (ClickUp Task-ების ანალოგი)
    """
    PRIORITY_CHOICES = (
        ('low', 'დაბალი (Low)'),
        ('medium', 'საშუალო (Medium)'),
        ('high', 'მაღალი (High)'),
        ('critical', 'კრიტიკული (Critical) 🛑'),
    )
    STATUS_CHOICES = (
        ('backlog', 'იდეა (Backlog)'),
        ('todo', 'გასაკეთებელი (Todo)'),
        ('in_progress', 'მიმდინარე (In Progress)'),
        ('review', 'შემოწმება (Review)'),
        ('done', 'შესრულებული (Done)'),
    )

    title = models.CharField(max_length=200, verbose_name="დავალება")
    description = models.TextField(verbose_name="დავალების დეტალები/აღწერა")
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name="პასუხისმგებელი პირი"
    )
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium', verbose_name="პრიორიტეტი")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo', verbose_name="სტატუსი")
    sprint = models.ForeignKey(
        Sprint,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name="ეტაპი (Sprint)"
    )
    due_date = models.DateField(null=True, blank=True, verbose_name="შესრულების ვადა")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "დავალება (Task)"
        verbose_name_plural = "📋 დავალებები (ClickUp Board)"
        ordering = ['-priority', 'due_date']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"


class ProjectWiki(models.Model):
    """
    პროექტის დოკუმენტაცია, სტრუქტურა და ბრენდინგის ხედვა (სრულყოფილი Wiki)
    """
    CATEGORY_CHOICES = (
        ('branding', 'ბრენდინგი & დიზაინი (Branding & Design)'),
        ('architecture', 'არქიტექტურა & სტრუქტურა (Architecture)'),
        ('general', 'ზოგადი წესები (General Guidelines)'),
    )

    title = models.CharField(max_length=150, verbose_name="დოკუმენტის სახელი")
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default='general', verbose_name="კატეგორია")
    content = models.TextField(verbose_name="შინაარსი (Markdown მხარდაჭერით)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="განახლდა")

    class Meta:
        verbose_name = "დოკუმენტი (Wiki)"
        verbose_name_plural = "📖 პროექტის დოკუმენტაცია (Wiki)"

    def __str__(self):
        return f"{self.get_category_display()} - {self.title}"
