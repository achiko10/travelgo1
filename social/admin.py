from django.contrib import admin
from django.utils.html import format_html
from .models import Friendship, FriendActivity, ChallengeInvite


@admin.register(Friendship)
class FriendshipAdmin(admin.ModelAdmin):
    list_display  = ('from_user', 'to_user', 'status', 'created_at')
    list_filter   = ('status',)
    search_fields = ('from_user__email', 'to_user__email')
    list_editable = ('status',)
    ordering      = ('-created_at',)
    raw_id_fields = ('from_user', 'to_user')


@admin.register(FriendActivity)
class FriendActivityAdmin(admin.ModelAdmin):
    list_display  = ('user', 'activity_badge', 'activity_type', 'poi', 'badge', 'xp_earned', 'created_at')
    list_filter   = ('activity_type',)
    search_fields = ('user__email',)
    ordering      = ('-created_at',)
    raw_id_fields = ('user', 'poi', 'badge', 'skin')
    readonly_fields = ('created_at',)

    def activity_badge(self, obj):
        colors = {
            'checkin':         '#006749',
            'level_up':        '#FFB400',
            'badge_earned':    '#9B59B6',
            'quest_completed': '#27AE60',
            'skin_unlocked':   '#3498DB',
            'joined':          '#E67E22',
        }
        color = colors.get(obj.activity_type, '#95A5A6')
        label = obj.get_activity_type_display()
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:11px">{}</span>',
            color, label
        )
    activity_badge.short_description = "ტიპი"


@admin.register(ChallengeInvite)
class ChallengeInviteAdmin(admin.ModelAdmin):
    list_display  = ('from_user', 'to_user', 'poi', 'status', 'status_badge', 'bonus_xp', 'created_at', 'expires_at')
    list_display_links = ('from_user', 'to_user')
    list_filter   = ('status',)
    search_fields = ('from_user__email', 'to_user__email', 'poi__name')
    list_editable = ('status',)
    ordering      = ('-created_at',)
    raw_id_fields = ('from_user', 'to_user', 'poi')
    readonly_fields = ('created_at', 'completed_at')

    def status_badge(self, obj):
        colors = {
            'pending':   '#F39C12',
            'accepted':  '#27AE60',
            'declined':  '#E74C3C',
            'completed': '#006749',
            'expired':   '#7F8C8D',
        }
        color = colors.get(obj.status, '#95A5A6')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "სტატუსი"
