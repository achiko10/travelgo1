from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Badge, Skin, UserInventory


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """
    Badge — მოგზაური იღებს Check-in-ებით, Quest-ებით ან სპეციალური
    ლოკაციების მოსანახულებლად.
    """
    list_display = ('name', 'rarity', 'rarity_colored', 'coin_price', 'is_for_sale', 'description_short', 'has_image')
    list_filter = ('rarity', 'is_for_sale')
    list_editable = ('coin_price', 'is_for_sale')
    search_fields = ('name', 'description')

    fieldsets = (
        ('🏅 Badge ინფო (KA)', {
            'fields': ('name', 'description', 'rarity', 'image')
        }),
        ('🌐 ინგლისური (EN)', {
            'fields': ('name_en', 'description_en'),
            'classes': ('collapse',)
        }),
        ('🛒 Rewards მაღაზია', {
            'fields': ('is_for_sale', 'coin_price')
        }),
    )

    RARITY_COLORS = {
        'common':    '#95a5a6',
        'rare':      '#3498db',
        'epic':      '#9b59b6',
        'legendary': '#f39c12',
    }

    def rarity_colored(self, obj):
        color = self.RARITY_COLORS.get(obj.rarity, '#fff')
        label = obj.get_rarity_display()
        return format_html(
            '<span style="color:{};font-weight:bold">⭐ {}</span>', color, label
        )
    rarity_colored.short_description = "სიშვიათე"

    def description_short(self, obj):
        return obj.description[:60] + '…' if len(obj.description) > 60 else obj.description
    description_short.short_description = "აღწერა"

    def has_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url
            )
        return format_html('<span style="color:#aaa">— არა</span>')
    has_image.short_description = "სურათი"


@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    """
    Skin — Avatar-ის კოსტიუმი/სახე. განბლოკდება კონკრეტულ
    რეგიონში Check-in-ებით.
    """
    list_display = ('name', 'region_unlock', 'coin_price', 'is_for_sale', 'description_short', 'has_image')
    list_filter = ('is_for_sale',)
    list_editable = ('coin_price', 'is_for_sale')
    search_fields = ('name', 'description', 'region_unlock')

    fieldsets = (
        ('👗 Skin ინფო (KA)', {
            'fields': ('name', 'description', 'region_unlock', 'image')
        }),
        ('🌐 ინგლისური (EN)', {
            'fields': ('name_en', 'description_en', 'region_unlock_en'),
            'classes': ('collapse',)
        }),
        ('🛒 Rewards მაღაზია', {
            'fields': ('is_for_sale', 'coin_price')
        }),
    )

    def description_short(self, obj):
        return obj.description[:60] + '…' if len(obj.description) > 60 else obj.description
    description_short.short_description = "აღწერა"

    def has_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px;" />', obj.image.url
            )
        return format_html('<span style="color:#aaa">— არა</span>')
    has_image.short_description = "სურათი"


@admin.register(UserInventory)
class UserInventoryAdmin(admin.ModelAdmin):
    """
    UserInventory — რომელ მომხმარებელს რომელი Badge/Skin აქვს
    და სად განბლოკა.
    """
    list_display = (
        'user', 'item_name', 'item_type', 'location_unlocked_from', 'date_unlocked'
    )
    list_filter = ('date_unlocked',)
    search_fields = ('user__email', 'badge__name', 'skin__name', 'location_unlocked_from')
    readonly_fields = ('date_unlocked', 'user', 'badge', 'skin', 'location_unlocked_from')
    date_hierarchy = 'date_unlocked'

    def item_name(self, obj):
        if obj.badge:
            return format_html('<b>{}</b>', '[Badge] ' + obj.badge.name)
        if obj.skin:
            return format_html('<b>{}</b>', '[Skin] ' + obj.skin.name)
        return '—'
    item_name.short_description = "Item"

    def item_type(self, obj):
        if obj.badge:
            return mark_safe('<span style="color:#f39c12;font-weight:bold">Badge</span>')
        if obj.skin:
            return mark_safe('<span style="color:#9b59b6;font-weight:bold">Skin</span>')
        return '—'
    item_type.short_description = "Type"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
