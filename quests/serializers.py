from rest_framework import serializers
from .models import DailyQuest, UserQuestProgress
from travelgo_core.translation_utils import get_translated
from maps.serializers import POISerializer

class DailyQuestSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    target_poi = POISerializer(read_only=True)

    class Meta:
        model = DailyQuest
        fields = ['id', 'title', 'description', 'reward_xp', 'reward_coins', 'target_poi', 'required_checkins', 'date_active']

    def get_title(self, obj):
        return get_translated(obj, 'title', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))


class UserQuestProgressSerializer(serializers.ModelSerializer):
    quest = DailyQuestSerializer(read_only=True)
    
    class Meta:
        model = UserQuestProgress
        fields = '__all__'
