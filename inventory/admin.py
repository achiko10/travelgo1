from django.contrib import admin
from .models import Badge, Skin, UserInventory

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity')

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('name', 'region_unlock')

@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'skin', 'date_unlocked')
