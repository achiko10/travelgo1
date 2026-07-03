from rest_framework import serializers
from .models import Category, Partner, DiscountCoupon
from travelgo_core.translation_utils import get_translated

class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon_name']

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))


class PartnerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    terms_and_conditions = serializers.SerializerMethodField()
    location_address = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Partner
        fields = [
            'id', 'name', 'description', 'terms_and_conditions', 'category',
            'category_name', 'logo', 'location_address', 'latitude',
            'longitude', 'offer_percentage'
        ]

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))

    def get_terms_and_conditions(self, obj):
        return get_translated(obj, 'terms_and_conditions', self.context.get('request'))

    def get_location_address(self, obj):
        return get_translated(obj, 'location_address', self.context.get('request'))

    def get_category_name(self, obj):
        return get_translated(obj.category, 'name', self.context.get('request'))


class DiscountCouponSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)

    class Meta:
        model = DiscountCoupon
        fields = ['id', 'partner', 'code', 'discount_pct', 'status', 'valid_until', 'created_at']
