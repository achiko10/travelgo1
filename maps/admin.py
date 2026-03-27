from django.contrib import admin
from .models import PointOfInterest, RedZone, CheckIn

@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    list_display = ('name', 'poi_type', 'base_xp', 'latitude', 'longitude')
    list_filter = ('poi_type',)
    search_fields = ('name',)

@admin.register(RedZone)
class RedZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'latitude', 'longitude', 'radius_meters')

@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ('user', 'poi', 'awarded_xp', 'timestamp')
    readonly_fields = ('timestamp',)
