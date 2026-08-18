from rest_framework import serializers
from .models import Landmark, EcoMission, WasteType, UserMissionProgress


class LandmarkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Landmark
        fields = '__all__'


class WasteTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = WasteType
        fields = ['id', 'waste_type', 'qr_code_value']


class EcoMissionSerializer(serializers.ModelSerializer):
    waste_types = WasteTypeSerializer(many=True, read_only=True)
    is_campaign_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = EcoMission
        fields = '__all__'


class UserMissionProgressSerializer(serializers.ModelSerializer):
    mission_title = serializers.CharField(source='mission.title', read_only=True)
    mission_id_str = serializers.CharField(source='mission.mission_id', read_only=True)

    class Meta:
        model = UserMissionProgress
        fields = [
            'id', 'user', 'mission', 'mission_title', 'mission_id_str',
            'status', 'qr_scanned_count', 'photo_uploaded',
            'gps_points_visited', 'xp_earned', 'started_at', 'completed_at',
        ]
        read_only_fields = ['user', 'started_at', 'completed_at']
