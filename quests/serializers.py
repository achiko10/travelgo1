from rest_framework import serializers
from .models import DailyQuest, UserQuestProgress

class DailyQuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyQuest
        fields = '__all__'

class UserQuestProgressSerializer(serializers.ModelSerializer):
    quest = DailyQuestSerializer(read_only=True)
    
    class Meta:
        model = UserQuestProgress
        fields = '__all__'
