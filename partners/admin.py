from django.contrib import admin
from .models import Category, Partner

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_name')

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'offer_percentage', 'location_address')
    list_filter = ('category',)
    search_fields = ('name',)
