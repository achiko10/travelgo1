from django.contrib import admin
from django.utils.html import format_html
from .models import SystemConfig, OnboardingSlide, AppTranslation, ARTutorialStep

@admin.register(SystemConfig)
class SystemConfigAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'checkin_radius_meters', 'referral_bonus_xp', 'referral_bonus_coins', 'app_maintenance_mode', 'min_app_version')

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return True

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(OnboardingSlide)
class OnboardingSlideAdmin(admin.ModelAdmin):
    list_display = ('step_number', 'title', 'is_active', 'slide_preview')
    list_display_links = ('title',)
    list_editable = ('is_active', 'step_number')
    ordering = ('step_number',)

    def slide_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height:40px;border-radius:4px;" />', obj.image.url)
        return "ფოტოს გარეშე"
    slide_preview.short_description = "სურათი"


@admin.register(AppTranslation)
class AppTranslationAdmin(admin.ModelAdmin):
    list_display = ('key', 'category', 'text_ka', 'text_en')
    list_filter = ('category',)
    search_fields = ('key', 'text_ka', 'text_en')
    list_editable = ('text_ka', 'text_en')


@admin.register(ARTutorialStep)
class ARTutorialStepAdmin(admin.ModelAdmin):
    list_display = ('step_number', 'target_action', 'instruction_ka', 'lottie_animation_name', 'is_active')
    list_display_links = ('step_number', 'target_action')
    list_editable = ('is_active',)
    list_filter = ('target_action', 'is_active')
    search_fields = ('instruction_ka', 'instruction_en', 'lottie_animation_name')
