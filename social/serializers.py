from rest_framework import serializers
from .models import Friendship, FriendActivity, ChallengeInvite
from django.conf import settings


class FriendshipSerializer(serializers.ModelSerializer):
    from_user_email = serializers.ReadOnlyField(source='from_user.email')
    to_user_email   = serializers.ReadOnlyField(source='to_user.email')

    class Meta:
        model  = Friendship
        fields = ['id', 'from_user_email', 'to_user_email', 'status', 'created_at']


class FriendActivitySerializer(serializers.ModelSerializer):
    user_email  = serializers.ReadOnlyField(source='user.email')
    user_name   = serializers.ReadOnlyField(source='user.full_name')
    poi_name    = serializers.SerializerMethodField()
    badge_name  = serializers.SerializerMethodField()
    skin_name   = serializers.SerializerMethodField()

    class Meta:
        model  = FriendActivity
        fields = ['id', 'user_email', 'user_name', 'activity_type', 'poi_name', 'badge_name', 'skin_name', 'xp_earned', 'new_level', 'created_at']

    def get_poi_name(self, obj):
        return obj.poi.name if obj.poi else None

    def get_badge_name(self, obj):
        return obj.badge.name if obj.badge else None

    def get_skin_name(self, obj):
        return obj.skin.name if obj.skin else None


class ChallengeInviteSerializer(serializers.ModelSerializer):
    from_user_email = serializers.ReadOnlyField(source='from_user.email')
    to_user_email   = serializers.ReadOnlyField(source='to_user.email')
    poi_name        = serializers.ReadOnlyField(source='poi.name')

    class Meta:
        model  = ChallengeInvite
        fields = ['id', 'from_user_email', 'to_user_email', 'poi_name', 'message', 'status', 'bonus_xp', 'created_at', 'expires_at']
