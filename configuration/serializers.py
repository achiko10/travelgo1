from rest_framework import serializers
from .models import OnboardingSlide, SystemConfig, AppTranslation, ARTutorialStep
from travelgo_core.translation_utils import get_translated

class OnboardingSlideSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()

    class Meta:
        model = OnboardingSlide
        fields = ['id', 'title', 'description', 'image', 'step_number']

    def get_title(self, obj):
        return get_translated(obj, 'title', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))


class SystemConfigSerializer(serializers.ModelSerializer):
    app_name = serializers.SerializerMethodField()
    maintenance_message = serializers.SerializerMethodField()

    class Meta:
        model = SystemConfig
        fields = ['checkin_radius_meters', 'referral_bonus_xp', 'referral_bonus_coins', 'app_maintenance_mode', 'min_app_version', 'app_name', 'maintenance_message']

    def get_app_name(self, obj):
        return get_translated(obj, 'app_name', self.context.get('request'))

    def get_maintenance_message(self, obj):
        return get_translated(obj, 'maintenance_message', self.context.get('request'))


class ARTutorialStepSerializer(serializers.ModelSerializer):
    instruction = serializers.SerializerMethodField()

    class Meta:
        model = ARTutorialStep
        fields = ['id', 'step_number', 'target_action', 'instruction', 'lottie_animation_name']

    def get_instruction(self, obj):
        return get_translated(obj, 'instruction', self.context.get('request'))
