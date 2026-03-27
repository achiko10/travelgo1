from rest_framework import serializers
from .models import PointOfInterest, RedZone

class POISerializer(serializers.ModelSerializer):
    class Meta:
        model = PointOfInterest
        fields = '__all__'

class RedZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = RedZone
        fields = '__all__'

class CheckInRequestSerializer(serializers.Serializer):
    poi_id = serializers.IntegerField()
    user_lat = serializers.FloatField()
    user_lon = serializers.FloatField()
