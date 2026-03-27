from rest_framework import serializers
from .models import Badge, Skin, UserInventory

class BadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = '__all__'

class SkinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skin
        fields = '__all__'

class UserInventorySerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    skin = SkinSerializer(read_only=True)
    
    class Meta:
        model = UserInventory
        fields = '__all__'
