from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import PointOfInterest, RedZone, CheckIn
from quests.models import DailyQuest


# ── Inline: ჩექინები ამ ლოკაციაზე ─────────────────────────────────────────────
class POI_CheckInInline(admin.TabularInline):
    model = CheckIn
    extra = 0
    fields = ('user', 'awarded_xp', 'timestamp')
    readonly_fields = ('user', 'awarded_xp', 'timestamp')
    verbose_name = "ჩექინი"
    verbose_name_plural = "📍 განხორციელებული ჩექინები (Check-Ins)"
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


# ── Inline: ქვესთები ამ ლოკაციაზე ─────────────────────────────────────────────
class POI_DailyQuestInline(admin.TabularInline):
    model = DailyQuest
    fk_name = 'target_poi'
    extra = 0
    fields = ('title', 'reward_xp', 'reward_coins', 'date_active')
    readonly_fields = ('title', 'reward_xp', 'reward_coins', 'date_active')
    verbose_name = "დაკავშირებული ქვესთი"
    verbose_name_plural = "🎮 ამ ლოკაციის ქვესთები (Daily Quests)"
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(PointOfInterest)
class PointOfInterestAdmin(admin.ModelAdmin):
    inlines = [POI_CheckInInline, POI_DailyQuestInline]

    """
    ლოკაციების (POI) მართვა — ადმინ ამატებს ლოკაციებს, რომლებიც
    Flutter Map-ზე გამოჩნდება და Check-in-ის სამიზნეა.
    """
    list_display = (
        'name', 'poi_type', 'base_xp', 'latitude', 'longitude',
        'open_hours', 'reward_badge_name', 'has_audio_guide',
        'has_photo', 'checkin_count'
    )
    list_filter = ('poi_type',)
    search_fields = ('name', 'description', 'reward_badge_name')
    readonly_fields = ('checkin_count', 'photo_preview', 'google_maps_preview')

    fieldsets = (
        ('📍 ძირითადი ინფო', {
            'fields': ('name', 'description', 'poi_type', 'open_hours')
        }),
        ('🗺️ კოორდინატები', {
            'fields': ('latitude', 'longitude', 'google_maps_link', 'google_maps_preview')
        }),
        ('🎁 ჯილდო / Drop System', {
            'fields': ('base_xp', 'reward_badge_name'),
            'description': 'reward_badge_name — Badge ან Skin-ის სახელი (ზუსტად ისე, '
                           'როგორც Inventory-ში), Check-in-ისას ავტომატურად გადაეცემა მომხმარებელს.'
        }),
        ('📸 მედია', {
            'fields': ('photo', 'photo_preview', 'audio_guide'),
        }),
        ('📊 სტატისტიკა', {
            'fields': ('checkin_count',),
        }),
    )

    # ── Custom columns ──────────────────────────────────────────────────
    def has_audio_guide(self, obj):
        if obj.audio_guide:
            return mark_safe('<span style="color:#2ecc71">&#127925; კი</span>')
        return mark_safe('<span style="color:#aaa">&#8212;</span>')
    has_audio_guide.short_description = "აუდიო"

    def has_photo(self, obj):
        if obj.photo:
            return mark_safe('<span style="color:#2ecc71">&#128248; კი</span>')
        return mark_safe('<span style="color:#aaa">&#8212;</span>')
    has_photo.short_description = "ფოტო"

    def checkin_count(self, obj):
        count = obj.checkins.count()
        return format_html('<b style="color:#3498db">{}</b>', str(count) + ' Check-in')
    checkin_count.short_description = "Check-ins"

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:8px;" />', obj.photo.url
            )
        return '—'
    photo_preview.short_description = "ფოტოს Preview"

    def google_maps_preview(self, obj):
        if obj.google_maps_link:
            return format_html(
                '<a href="{}" target="_blank">Google Maps</a>',
                obj.google_maps_link
            )
        return '—'
    google_maps_preview.short_description = "Google Maps"


@admin.register(RedZone)
class RedZoneAdmin(admin.ModelAdmin):
    """
    Anti-Scam Red Zones — Flutter Map-ზე წითლად ჩანს.
    მომხმარებელი გაფრთხილდება ამ ადგილებში.
    """
    list_display = ('name', 'latitude', 'longitude', 'radius_meters', 'danger_level')
    list_filter = ('radius_meters',)
    search_fields = ('name',)

    fieldsets = (
        ('⚠️ Red Zone ინფო', {
            'fields': ('name',)
        }),
        ('📍 კოორდინატები და ზომა', {
            'fields': ('latitude', 'longitude', 'radius_meters'),
            'description': 'radius_meters — ზონის რადიუსი მეტრებში. '
                           'Flutter Map-ი ამ მონაცემს იღებს API-ს გავლით.'
        }),
    )

    def danger_level(self, obj):
        r = obj.radius_meters
        if r >= 500:
            return format_html('<span style="color:#e74c3c;font-weight:bold">{}</span>', 'HIGH (' + str(r) + 'm)')
        elif r >= 100:
            return format_html('<span style="color:#e67e22;font-weight:bold">{}</span>', 'MED (' + str(r) + 'm)')
        else:
            return format_html('<span style="color:#f1c40f;font-weight:bold">{}</span>', 'LOW (' + str(r) + 'm)')
    danger_level.short_description = "Danger Level"


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    """
    Check-in ჩანაწერები — Anti-Cheat ლოგი.
    unique_together: ერთ ლოკაციაში ერთ მომხმარებელს მხოლოდ ერთხელ შეუძლია.
    ეს ჩანაწერები მხოლოდ API-ს გავლით იქმნება, ხელით ვერ დაამატებ.
    """
    list_display = ('user', 'poi', 'poi_type', 'awarded_xp', 'timestamp')
    list_filter = ('poi__poi_type', 'timestamp')
    search_fields = ('user__email', 'poi__name')
    readonly_fields = ('user', 'poi', 'awarded_xp', 'timestamp')
    date_hierarchy = 'timestamp'

    def poi_type(self, obj):
        return obj.poi.get_poi_type_display()
    poi_type.short_description = "ლოკაციის ტიპი"

    def has_add_permission(self, request):
        # Check-in-ები მხოლოდ API-ით იქმნება
        return False

    def has_change_permission(self, request, obj=None):
        return False
