from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import DailyQuest, UserQuestProgress, QuizQuestion, UserQuizSubmission, UserPuzzleSubmission


# ── Inline: ქვიზის კითხვები POI-სთვის ──────────────────────────────────────────
class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1
    fields = ('question', 'answer1', 'answer2', 'answer3', 'answer4', 'correct_index')


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('question', 'poi', 'correct_index')
    list_filter = ('poi',)
    search_fields = ('question', 'poi__name')


@admin.register(UserQuizSubmission)
class UserQuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'poi', 'score', 'date_submitted')
    list_filter = ('date_submitted', 'poi')
    search_fields = ('user__email', 'poi__name')


@admin.register(UserPuzzleSubmission)
class UserPuzzleSubmissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'poi', 'date_submitted')
    list_filter = ('date_submitted', 'poi')
    search_fields = ('user__email', 'poi__name')


# ── Inline: ქვესთის შესრულება ──────────────────────────────────────────────────

class QuestProgressInline(admin.TabularInline):
    model = UserQuestProgress
    extra = 0
    fields = ('user', 'progress', 'is_completed')
    readonly_fields = ('user', 'progress', 'is_completed')
    verbose_name = "მონაწილე"
    verbose_name_plural = "მომხმარებლების პროგრესი"
    can_delete = False
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(DailyQuest)
class DailyQuestAdmin(admin.ModelAdmin):
    inlines = [QuestProgressInline]

    list_display = (
        'title', 'date_active', 'reward_xp', 'reward_coins',
        'required_checkins', 'target_poi', 'completion_rate'
    )
    list_filter = ('date_active',)
    search_fields = ('title', 'description', 'target_poi__name')
    readonly_fields = ('completion_rate',)
    date_hierarchy = 'date_active'

    fieldsets = (
        ('Quest Info (KA)', {
            'fields': ('title', 'description')
        }),
        ('Quest Info (EN)', {
            'fields': ('title_en', 'description_en'),
            'classes': ('collapse',)
        }),
        ('Mizani / Goal', {
            'fields': ('target_poi', 'required_checkins', 'date_active')
        }),
        ('Jildo / Reward', {
            'fields': ('reward_xp', 'reward_coins')
        }),
        ('Statistika', {
            'fields': ('completion_rate',),
            'classes': ('collapse',),
        }),
    )

    def completion_rate(self, obj):
        total = obj.userquestprogress_set.count()
        completed = obj.userquestprogress_set.filter(is_completed=True).count()
        if total == 0:
            return '—'
        pct = int((completed / total) * 100)
        color = '#2ecc71' if pct >= 50 else '#e67e22' if pct >= 20 else '#e74c3c'
        return format_html(
            '<b style="color:{}">{}/{} ({}%)</b>',
            color, completed, total, pct
        )
    completion_rate.short_description = "Completion %"


@admin.register(UserQuestProgress)
class UserQuestProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'quest', 'progress', 'is_completed', 'status_icon')
    list_filter = ('is_completed', 'quest__date_active')
    search_fields = ('user__email', 'quest__title')
    readonly_fields = ('user', 'quest', 'progress', 'is_completed')

    def status_icon(self, obj):
        if obj.is_completed:
            return mark_safe('<span style="color:#2ecc71;font-size:1.1em;font-weight:bold">&#10003; Done</span>')
        return mark_safe('<span style="color:#e67e22">&#9203; In Progress</span>')
    status_icon.short_description = "Status"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
