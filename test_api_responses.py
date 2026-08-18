import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'travelgo_core.settings')
django.setup()

from partners.models import Partner, Category, DiscountCoupon
from quests.models import DailyQuest
from social.models import ChallengeInvite
from django.utils import timezone

print("--- PARTNERS ---")
partners = Partner.objects.all()
print(f"Total Partners in DB: {partners.count()}")
for p in partners:
    print(f"ID: {p.id}, Name: {p.name.encode('utf-8')}, Lat: {p.latitude}, Lon: {p.longitude}, Offer%: {p.offer_percentage}")

print("\n--- DAILY QUESTS ---")
today = timezone.now().date()
print(f"Today date: {today}")
quests = DailyQuest.objects.filter(date_active=today)
print(f"Daily Quests matching today ({today}): {quests.count()}")
all_quests = DailyQuest.objects.all()
print(f"Total Daily Quests in DB: {all_quests.count()}")
for q in all_quests:
    print(f"ID: {q.id}, Title: {q.title.encode('utf-8')}, date_active: {q.date_active}")

print("\n--- CHALLENGES ---")
challenges = ChallengeInvite.objects.all()
print(f"Total Challenge Invites in DB: {challenges.count()}")
for c in challenges:
    print(f"ID: {c.id}, From: {c.from_user.email}, To: {c.to_user.email}, POI: {c.poi.name.encode('utf-8')}, Status: {c.status}")
