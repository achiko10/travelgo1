from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Sprint, ProjectTask, ProjectWiki

# ── Inline: Tasks in Sprint ──────────────────────────────────────────────────
class ProjectTaskInline(admin.TabularInline):
    model = ProjectTask
    extra = 1
    fields = ('title', 'assignee', 'priority', 'status', 'due_date')
    verbose_name = "დავალება"
    verbose_name_plural = "📋 დაკავშირებული დავალებები"


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'task_completion_status', 'is_completed_badge')
    list_filter = ('is_completed',)
    search_fields = ('title', 'description')
    inlines = [ProjectTaskInline]

    def is_completed_badge(self, obj):
        if obj.is_completed:
            return mark_safe('<span style="background:#2ecc71;color:white;padding:3px 8px;border-radius:4px;font-weight:bold">&#10003; Done</span>')
        return mark_safe('<span style="background:#e67e22;color:white;padding:3px 8px;border-radius:4px;font-weight:bold">&#9203; Active</span>')
    is_completed_badge.short_description = "Status"

    def task_completion_status(self, obj):
        total = obj.tasks.count()
        done = obj.tasks.filter(status='done').count()
        if total == 0:
            return "დავალებების გარეშე"
        percent = int((done / total) * 100)
        color = "#2ecc71" if percent == 100 else "#3498db" if percent > 50 else "#e74c3c"
        return format_html(
            '<div style="width:100px;background:#ddd;border-radius:3px;overflow:hidden;display:inline-block;vertical-align:middle;margin-right:8px">'
            '<div style="width:{}px;height:10px;background:{}"></div>'
            '</div><b>{}%</b> ({}/{})',
            percent, color, percent, done, total
        )
    task_completion_status.short_description = "შესრულება"


@admin.register(ProjectTask)
class ProjectTaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'sprint', 'assignee', 'priority_colored', 'status_badge', 'due_date_status')
    list_filter = ('status', 'priority', 'sprint', 'assignee')
    search_fields = ('title', 'description')
    date_hierarchy = 'due_date'

    # Bulk status updates
    actions = ['mark_done', 'mark_in_progress', 'mark_review']

    def priority_colored(self, obj):
        colors = {
            'low': ('#95a5a6', 'დაბალი'),
            'medium': ('#3498db', 'საშუალო'),
            'high': ('#e67e22', 'მაღალი'),
            'critical': ('#e74c3c', '🛑 კრიტიკული'),
        }
        color, text = colors.get(obj.priority, ('#fff', obj.priority))
        return format_html('<b style="color:{}">{}</b>', color, text)
    priority_colored.short_description = "პრიორიტეტი"

    def status_badge(self, obj):
        badges = {
            'backlog': '#7f8c8d',
            'todo': '#34495e',
            'in_progress': '#2980b9',
            'review': '#9b59b6',
            'done': '#27ae60',
        }
        color = badges.get(obj.status, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;font-size:0.9em;font-weight:bold">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = "სტატუსი"

    def due_date_status(self, obj):
        if not obj.due_date:
            return "—"
        from datetime import date
        today = date.today()
        if obj.status == 'done':
            return format_html('<span style="color:#27ae60">{}</span>', obj.due_date)
        if obj.due_date < today:
            return format_html('<b style="color:#c0392b">{}</b>', 'OVERDUE (' + str(obj.due_date) + ')')
        return str(obj.due_date)
    due_date_status.short_description = "ვადა"

    # Actions
    def mark_done(self, request, queryset):
        queryset.update(status='done')
        self.message_user(request, "მონიშნული დავალებები გადავიდა Done სტატუსში.")
    mark_done.short_description = "✅ სტატუსი: შესრულებული (Done)"

    def mark_in_progress(self, request, queryset):
        queryset.update(status='in_progress')
        self.message_user(request, "მონიშნული დავალებები გადავიდა In Progress სტატუსში.")
    mark_in_progress.short_description = "⏳ სტატუსი: მიმდინარე (In Progress)"

    def mark_review(self, request, queryset):
        queryset.update(status='review')
        self.message_user(request, "მონიშნული დავალებები გადავიდა Review სტატუსში.")
    mark_review.short_description = "🔍 სტატუსი: შემოწმება (Review)"


@admin.register(ProjectWiki)
class ProjectWikiAdmin(admin.ModelAdmin):
    list_display = ('title', 'category_badge', 'updated_at')
    list_filter = ('category',)
    search_fields = ('title', 'content')
    readonly_fields = ('wiki_preview',)

    fieldsets = (
        ('📖 დოკუმენტი', {
            'fields': ('title', 'category', 'content')
        }),
        ('🖥️ Preview', {
            'fields': ('wiki_preview',),
            'description': 'ავტომატური Preview ფორმატირებული სახით'
        }),
    )

    def category_badge(self, obj):
        colors = {
            'branding': '#006749',
            'architecture': '#2e3a46',
            'general': '#7f8c8d',
        }
        color = colors.get(obj.category, '#7f8c8d')
        return format_html(
            '<span style="background:{};color:white;padding:3px 8px;border-radius:4px;font-weight:bold">{}</span>',
            color, obj.get_category_display()
        )
    category_badge.short_description = "კატეგორია"

    def wiki_preview(self, obj):
        if not obj.content:
            return "ცარიელია"
        # მარტივი HTML rendering markdown-ის ნაცვლად, რათა ლამაზად გამოჩნდეს ადმინში
        import html
        escaped = html.escape(obj.content).replace('\n', '<br>')
        return mark_safe(f'<div style="background:#f9f9f9;padding:15px;border:1px solid #ddd;border-radius:4px;max-height:400px;overflow-y:auto;font-family:sans-serif">{escaped}</div>')
    wiki_preview.short_description = "დოკუმენტის Preview"
