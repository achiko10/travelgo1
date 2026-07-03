from rest_framework import serializers
from .models import Badge, Skin, UserInventory
from travelgo_core.translation_utils import get_translated

class BadgeSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = Badge
        fields = ['id', 'name', 'description', 'image', 'rarity']

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))


class SkinSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    region_unlock = serializers.SerializerMethodField()

    class Meta:
        model = Skin
        fields = ['id', 'name', 'description', 'image', 'region_unlock']

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))

    def get_region_unlock(self, obj):
        return get_translated(obj, 'region_unlock', self.context.get('request'))


class UserInventorySerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    skin = SkinSerializer(read_only=True)
    
    class Meta:
        model = UserInventory
        fields = '__all__'
