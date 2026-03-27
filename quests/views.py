from rest_framework import generics, permissions
from django.utils import timezone
from .models import DailyQuest, UserQuestProgress
from .serializers import DailyQuestSerializer, UserQuestProgressSerializer

class ActiveQuestsList(generics.ListAPIView):
    """
    Returns only the quests that are generated for today.
    """
    serializer_class = DailyQuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyQuest.objects.filter(date_active=timezone.now().date())

class MyQuestProgress(generics.ListAPIView):
    serializer_class = UserQuestProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserQuestProgress.objects.filter(user=self.request.user)
