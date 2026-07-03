from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Category, Partner, DiscountCoupon


# ── Inline: კუპონები პარტნიორის გვერდზე ──────────────────────────────────────
class DiscountCouponInline(admin.TabularInline):
    model   = DiscountCoupon
    extra   = 1
    fields  = ('code', 'user', 'discount_pct', 'status', 'valid_until')
    readonly_fields = ('code',)
    verbose_name        = "კუპონი"
    verbose_name_plural = "კუპონები"
    show_change_link    = True


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'name_en', 'icon_name', 'partner_count')
    search_fields = ('name', 'name_en')

    def partner_count(self, obj):
        count = obj.partners.count()
        return format_html('<b>{}</b>', str(count) + ' პარტნიორი')
    partner_count.short_description = "პარტნიორები"


@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    inlines     = [DiscountCouponInline]
    list_display = (
        'name', 'name_en', 'category', 'offer_percentage_display',
        'location_address', 'active_coupon_count', 'has_logo'
    )
    list_filter   = ('category',)
    search_fields = ('name', 'name_en', 'location_address', 'description')

    fieldsets = (
        ('Biznes Info (KA)', {
            'fields': ('name', 'description', 'terms_and_conditions', 'category', 'logo')
        }),
        ('Business Info (EN)', {
            'fields': ('name_en', 'description_en', 'terms_and_conditions_en'),
            'classes': ('collapse',)
        }),
        ('Mdebareoba / Location', {
            'fields': ('location_address', 'location_address_en', 'latitude', 'longitude')
        }),
        ('Shetavazeba / Offer', {
            'fields': ('offer_percentage',)
        }),
    )

    def offer_percentage_display(self, obj):
        pct = obj.offer_percentage
        color = '#2ecc71' if pct >= 20 else '#3498db' if pct >= 10 else '#95a5a6'
        return format_html('<b style="color:{}">{}</b>', color, str(pct) + '%')
    offer_percentage_display.short_description = "Fasdaleba %"

    def active_coupon_count(self, obj):
        count = obj.coupons.filter(status='active').count()
        if count == 0:
            return format_html('<span style="color:#aaa">{}</span>', '0 kuponi')
        return format_html('<b style="color:#2ecc71">{}</b>', str(count) + ' kuponi')
    active_coupon_count.short_description = "Aqtiuri Kuponevi"

    def has_logo(self, obj):
        if obj.logo:
            return format_html('<img src="{}" style="height:35px;border-radius:4px;" />', obj.logo.url)
        return format_html('<span style="color:#aaa">{}</span>', '—')
    has_logo.short_description = "Logo"


@admin.register(DiscountCoupon)
class DiscountCouponAdmin(admin.ModelAdmin):
    """
    კუპონების სრული მართვა — ადმინი ქმნის, კოდი ავტომატურად გენერდება.
    Flutter-ი Check-in-ის შემდეგ აჩვენებს კოდს.
    """
    list_display  = (
        'code_display', 'partner', 'user', 'discount_pct',
        'status_colored', 'valid_until', 'created_at'
    )
    list_filter   = ('status', 'partner', 'valid_until')
    search_fields = ('code', 'partner__name', 'user__email')
    readonly_fields = ('code', 'created_at', 'used_at')
    date_hierarchy  = 'created_at'

    fieldsets = (
        ('Kuponis Info', {
            'fields': ('partner', 'user', 'code'),
            'description': 'code — avtomaturad gendeba shenakvvisas. '
                           'user — carelia tu nebismier momkhmarebels sheuzlia gamoyeneba.'
        }),
        ('Shetavazeba', {
            'fields': ('discount_pct', 'valid_until')
        }),
        ('Statusi', {
            'fields': ('status', 'created_at', 'used_at')
        }),
    )

    actions = ['mark_expired', 'generate_bulk_coupons']

    def code_display(self, obj):
        return format_html(
            '<code style="background:#1a1a2e;color:#f39c12;padding:3px 8px;'
            'border-radius:4px;font-size:1.1em;letter-spacing:1px">{}</code>',
            obj.code
        )
    code_display.short_description = "Kuponis Kodi"

    def status_colored(self, obj):
        colors = {'active': '#2ecc71', 'used': '#95a5a6', 'expired': '#e74c3c'}
        color  = colors.get(obj.status, '#fff')
        label  = obj.get_status_display()
        return format_html('<b style="color:{}">{}</b>', color, label)
    status_colored.short_description = "Statusi"

    @admin.action(description="Mark selected coupons as EXPIRED")
    def mark_expired(self, request, queryset):
        updated = queryset.update(status='expired')
        self.message_user(request, str(updated) + ' kuponi gatisulia.')

    @admin.action(description="Auto-generate 10 coupons per selected partner")
    def generate_bulk_coupons(self, request, queryset):
        count = 0
        for partner in queryset:
            for _ in range(10):
                DiscountCoupon.objects.create(partner=partner, discount_pct=partner.offer_percentage)
                count += 1
        self.message_user(request, str(count) + ' akhali kuponi sheiqmna!')
