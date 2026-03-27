from celery import shared_task
from django.utils import timezone
from .models import DailyQuest

@shared_task
def generate_daily_quests():
    """
    Celery task that should run via Celery Beat every day at 00:00 midnight.
    It automatically generates a random daily quest and pushes it to active clients.
    """
    # Simple hardcoded generation for MVP Server testing
    quest = DailyQuest.objects.create(
        title=f"Mystery Quest for {timezone.now().date()}",
        description="Visit 2 new locations today to earn bonus rewards!",
        reward_xp=300,
        reward_coins=50,
        required_checkins=2
    )
    return str(quest.title)
