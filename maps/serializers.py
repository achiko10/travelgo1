from rest_framework import serializers
from .models import PointOfInterest, RedZone
from travelgo_core.translation_utils import get_translated

class POISerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    open_hours = serializers.SerializerMethodField()
    audio_guide = serializers.SerializerMethodField()

    checkin_count = serializers.SerializerMethodField()
    reward_badge_name = serializers.SerializerMethodField()
    reward_skin_name = serializers.SerializerMethodField()

    class Meta:
        model = PointOfInterest
        fields = [
            'id', 'name', 'description', 'photo', 'audio_guide',
            'open_hours', 'poi_type', 'latitude', 'longitude',
            'base_xp', 'reward_badge', 'reward_badge_name',
            'reward_skin', 'reward_skin_name',
            'google_maps_link', 'checkin_count'
        ]

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))

    def get_open_hours(self, obj):
        return get_translated(obj, 'open_hours', self.context.get('request'))

    def get_audio_guide(self, obj):
        request = self.context.get('request')
        audio = get_translated(obj, 'audio_guide', request)
        if audio and hasattr(audio, 'url'):
            try:
                return request.build_absolute_uri(audio.url) if request else audio.url
            except (ValueError, AttributeError):
                return None
        return None

    def get_checkin_count(self, obj):
        return obj.checkins.count()

    def get_reward_badge_name(self, obj):
        return obj.reward_badge.name if obj.reward_badge else None

    def get_reward_skin_name(self, obj):
        return obj.reward_skin.name if obj.reward_skin else None


class RedZoneSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = RedZone
        fields = '__all__'

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))


class CheckInRequestSerializer(serializers.Serializer):
    poi_id = serializers.IntegerField()
    user_lat = serializers.FloatField()
    user_lon = serializers.FloatField()
