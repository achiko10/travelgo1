from django.contrib import admin
from .models import DailyQuest, UserQuestProgress

@admin.register(DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    list_display = ('title', 'date_active', 'reward_xp')
    list_filter = ('date_active',)

@admin.register(UserQuestProgress)
class UserQuestProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'is_completed')
