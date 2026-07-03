from rest_framework import serializers
from .models import CustomUser


class DigitalPassportSerializer(serializers.ModelSerializer):
    """Serializer for the complete Digital Passport — profile, gamification, inventory"""
    total_locations_visited = serializers.SerializerMethodField()
    unlocked_badges         = serializers.SerializerMethodField()
    unlocked_skins          = serializers.SerializerMethodField()
    total_referrals         = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = [
            # Auth / Contact
            'id', 'email', 'full_name', 'phone_number', 'profile_picture',
            # Location / Profile
            'country', 'city', 'traveler_type', 'interests', 'preferred_language',
            # Avatar
            'avatar_skin_color', 'avatar_hair_style', 'avatar_clothing',
            # Gamification
            'xp', 'level', 'coins',
            # Referral
            'referral_code', 'total_referrals',
            # Inventory
            'total_locations_visited', 'unlocked_badges', 'unlocked_skins',
        ]
        read_only_fields = ['xp', 'level', 'coins', 'referral_code']

    def get_total_locations_visited(self, obj):
        return obj.checkins.count() if hasattr(obj, 'checkins') else 0

    def get_unlocked_badges(self, obj):
        if hasattr(obj, 'inventory'):
            return [
                {
                    "name":     i.badge.name,
                    "rarity":   i.badge.rarity,
                    "location": i.location_unlocked_from,
                    "date":     i.date_unlocked,
                }
                for i in obj.inventory.filter(badge__isnull=False)
            ]
        return []

    def get_unlocked_skins(self, obj):
        if hasattr(obj, 'inventory'):
            return [
                {
                    "name":     i.skin.name,
                    "region":   i.skin.region_unlock,
                    "location": i.location_unlocked_from,
                    "date":     i.date_unlocked,
                }
                for i in obj.inventory.filter(skin__isnull=False)
            ]
        return []

    def get_total_referrals(self, obj):
        return obj.invited_users.count()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model  = CustomUser
        fields = ['email', 'password', 'full_name', 'phone_number']

    def create(self, validated_data):
        phone = validated_data.get('phone_number', '').strip()
        user  = CustomUser.objects.create_user(
            email        = validated_data['email'],
            password     = validated_data['password'],
            full_name    = validated_data.get('full_name', ''),
            phone_number = phone if phone else None
        )
        return user


# ── Alias used in views.py import ─────────────────────────────────────────────
ReferralDashboardSerializer = DigitalPassportSerializer


