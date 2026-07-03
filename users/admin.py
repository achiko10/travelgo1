from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import CustomUser, AnalyticsProxy

# ── იმპორტები სხვა აპებიდან Inlines-ისთვის ──────────────────────────────────
from maps.models import CheckIn
from inventory.models import UserInventory
from quests.models import UserQuestProgress
from partners.models import DiscountCoupon


# ── Inline: ვინ მოიწვია ეს user ──────────────────────────────────────────────
class InvitedUsersInline(admin.TabularInline):
    """Referral Tracking — ამ user-ის მიერ მოწვეული მეგობრების სია"""
    model         = CustomUser
    fk_name       = 'referred_by'
    extra         = 0
    fields        = ('email', 'full_name', 'level', 'xp', 'date_joined')
    readonly_fields = ('email', 'full_name', 'level', 'xp', 'date_joined')
    verbose_name  = "მოწვეული მეგობარი"
    verbose_name_plural = "👥 მოწვეული მეგობრები (Referral Tracking)"
    can_delete    = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


# ── Inline: მომხმარებლის ჩექინები ─────────────────────────────────────────────
class CheckInInline(admin.TabularInline):
    model = CheckIn
    extra = 0
    fields = ('poi', 'awarded_xp', 'timestamp')
    readonly_fields = ('poi', 'awarded_xp', 'timestamp')
    verbose_name = "ჩექინი"
    verbose_name_plural = "📍 განხორციელებული ჩექინები (Check-Ins)"
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


# ── Inline: მომხმარებლის ინვენტარი ────────────────────────────────────────────
class UserInventoryInline(admin.TabularInline):
    model = UserInventory
    extra = 0
    fields = ('badge', 'skin', 'location_unlocked_from', 'date_unlocked')
    readonly_fields = ('badge', 'skin', 'location_unlocked_from', 'date_unlocked')
    verbose_name = "ინვენტარი"
    verbose_name_plural = "🎒 ზურგჩანთა (Skins & Badges Inventory)"
    can_delete = True
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


# ── Inline: მომხმარებლის ქვესთების პროგრესი ────────────────────────────────────
class UserQuestProgressInline(admin.TabularInline):
    model = UserQuestProgress
    extra = 0
    fields = ('quest', 'progress', 'is_completed')
    readonly_fields = ('quest', 'progress', 'is_completed')
    verbose_name = "ქვესთის პროგრესი"
    verbose_name_plural = "🎮 ქვესთების პროგრესი (Quest Progress)"
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


# ── Inline: მომხმარებლის კუპონები ─────────────────────────────────────────────
class DiscountCouponInline(admin.TabularInline):
    model = DiscountCoupon
    extra = 0
    fields = ('code', 'partner', 'discount_pct', 'status', 'valid_until')
    readonly_fields = ('code', 'partner', 'discount_pct', 'status', 'valid_until')
    verbose_name = "კუპონი"
    verbose_name_plural = "🎟️ აქტიური/გამოყენებული კუპონები"
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model        = CustomUser
    inlines      = [InvitedUsersInline, CheckInInline, UserInventoryInline, UserQuestProgressInline, DiscountCouponInline]

    list_display = [
        'email', 'full_name', 'level', 'xp', 'coins',
        'referral_code', 'total_referrals', 'traveler_type',
        'is_active', 'is_staff'
    ]
    list_filter  = ('level', 'traveler_type', 'is_active', 'is_staff', 'preferred_language')
    ordering     = ['-xp']
    search_fields = ('email', 'full_name', 'phone_number', 'referral_code')
    readonly_fields = ('referral_code', 'date_joined', 'last_login', 'total_referrals')

    fieldsets = (
        ('🔑 ავტორიზაცია', {
            'fields': ('email', 'password')
        }),
        ('👤 პროფილი', {
            'fields': (
                'full_name', 'phone_number', 'profile_picture',
                'country', 'city', 'preferred_language',
                'traveler_type', 'interests'
            )
        }),
        ('🎨 Avatar სისტემა', {
            'fields': ('avatar_skin_color', 'avatar_hair_style', 'avatar_clothing'),
            'classes': ('collapse',),
        }),
        ('🎮 გეიმიფიკაცია (XP / Coins / Level)', {
            'fields': ('xp', 'level', 'coins')
        }),
        ('🔗 Referral სისტემა', {
            'fields': ('referral_code', 'referred_by', 'total_referrals'),
            'description': 'referral_code — ავტომატური 6-ნიშნა კოდი. '
                           'ქვემოთ ნახავთ ამ user-ის მიერ მოწვეული მეგობრების სიას.'
        }),
        ('🔐 წვდომა / Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
        ('📅 თარიღები', {
            'fields': ('date_joined', 'last_login'),
            'classes': ('collapse',),
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    def total_referrals(self, obj):
        count = obj.invited_users.count()
        if count == 0:
            return '—'
        return format_html('<b style="color:#3498db">{}</b>', str(count) + ' referrals')
    total_referrals.short_description = "Referrals"


@admin.register(AnalyticsProxy)
class AnalyticsProxyAdmin(admin.ModelAdmin):
    """
    Phase 8 — Admin Analytics Dashboard (Proxy Model)
    მხოლოდ კითხვის რეჟიმი — სტატისტიკა მომხმარებლებზე
    """
    list_display = (
        'email', 'full_name', 'level', 'xp', 'coins',
        'total_checkins', 'total_referrals_sent', 'date_joined_display', 'is_active'
    )
    list_filter   = ('level', 'is_active', 'traveler_type')
    search_fields = ('email', 'full_name')
    ordering      = ('-xp',)
    readonly_fields = [f.name for f in CustomUser._meta.get_fields()
                       if hasattr(f, 'name') and not f.is_relation]
    date_hierarchy = 'date_joined'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def total_checkins(self, obj):
        count = obj.checkins.count()
        return format_html('<b style="color:#2ecc71">{}</b>', str(count) + ' check-ins')
    total_checkins.short_description = "Check-ins"

    def total_referrals_sent(self, obj):
        count = obj.invited_users.count()
        return format_html('<b style="color:#3498db">{}</b>', str(count) + ' referrals')
    total_referrals_sent.short_description = "Referrals"

    def date_joined_display(self, obj):
        return obj.date_joined.strftime('%d %b %Y')
    date_joined_display.short_description = "📅 გაწევრება"





