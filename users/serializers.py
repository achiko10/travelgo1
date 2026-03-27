from rest_framework import serializers
from .models import CustomUser

class DigitalPassportSerializer(serializers.ModelSerializer):
    """ Serializer for the complete Digital Passport MVP """
    total_locations_visited = serializers.SerializerMethodField()
    unlocked_badges = serializers.SerializerMethodField()
    unlocked_skins = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'full_name', 'phone_number', 'profile_picture', 
            'country', 'city', 'traveler_type', 'interests',
            'xp', 'level', 'coins', 
            'total_locations_visited', 'unlocked_badges', 'unlocked_skins'
        ]
        read_only_fields = ['xp', 'level', 'coins']

    def get_total_locations_visited(self, obj):
        # Reverse query to maps CheckIn
        return obj.checkins.count() if hasattr(obj, 'checkins') else 0

    def get_unlocked_badges(self, obj):
        if hasattr(obj, 'inventory'):
            return [{"name": i.badge.name, "rarity": i.badge.rarity, "date": i.date_unlocked} 
                    for i in obj.inventory.filter(badge__isnull=False)]
        return []

    def get_unlocked_skins(self, obj):
        if hasattr(obj, 'inventory'):
            return [{"name": i.skin.name, "region": i.skin.region_unlock, "date": i.date_unlocked} 
                    for i in obj.inventory.filter(skin__isnull=False)]
        return []

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'full_name', 'phone_number']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            full_name=validated_data.get('full_name', ''),
            phone_number=validated_data.get('phone_number', '')
        )
        return user
