from django.urls import path
from .views import ActiveQuestsList, MyQuestProgress

urlpatterns = [
    path('daily/', ActiveQuestsList.as_view(), name='daily_quests'),
    path('my-progress/', MyQuestProgress.as_view(), name='my_quests'),
]
