from django.contrib import admin
from .models import Landmark, EcoMission, WasteType, UserMissionProgress


@admin.register(Landmark)
class LandmarkAdmin(admin.ModelAdmin):
    list_display = ('name_ka', 'category', 'address', 'latitude', 'longitude')
    list_filter = ('category',)
    search_fields = ('name_ka', 'name_en', 'address')


class WasteTypeInline(admin.TabularInline):
    model = WasteType
    extra = 1


@admin.register(EcoMission)
class EcoMissionAdmin(admin.ModelAdmin):
    list_display = ('mission_id', 'title', 'location_name', 'reward_xp', 'campaign_start_date', 'campaign_end_date')
    list_filter = ('campaign_start_date', 'campaign_end_date')
    search_fields = ('mission_id', 'title', 'location_name')
    inlines = [WasteTypeInline]


@admin.register(UserMissionProgress)
class UserMissionProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'mission', 'status', 'qr_scanned_count', 'photo_uploaded', 'xp_earned', 'completed_at')
    list_filter = ('status',)
    search_fields = ('user__email', 'mission__title')
    readonly_fields = ('started_at',)
