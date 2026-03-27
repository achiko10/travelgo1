from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, AnalyticsProxy

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'full_name', 'level', 'xp', 'is_staff']
    ordering = ['email']
    search_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Travel Profile', {'fields': ('full_name', 'phone_number', 'profile_picture', 'country', 'city', 'preferred_language', 'traveler_type', 'interests')}),
        ('Gamification (Level/XP)', {'fields': ('xp', 'level', 'coins')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)

@admin.register(AnalyticsProxy)
class AnalyticsProxyAdmin(admin.ModelAdmin):
    list_display = ('email', 'level', 'xp', 'total_checkins', 'total_referrals_sent')
    list_filter = ('level',)
    search_fields = ('email',)
    ordering = ('-xp',)
    
    def has_add_permission(self, request):
        return False
        
    def total_checkins(self, obj):
        return obj.checkins.count()
    total_checkins.short_description = "ჯამური ჩექინები"

    def total_referrals_sent(self, obj):
        return obj.invited_users.count()
    total_referrals_sent.short_description = "მოწვეული მეგობრები"
