from rest_framework import serializers
from .models import Category, Partner, PartnerPhoto, DiscountCoupon
from travelgo_core.translation_utils import get_translated


class CategorySerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'icon_name']

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))


class PartnerPhotoSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    caption = serializers.SerializerMethodField()

    class Meta:
        model = PartnerPhoto
        fields = ['id', 'image', 'caption', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image:
            url = obj.image.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None

    def get_caption(self, obj):
        return get_translated(obj, 'caption', self.context.get('request'))


class PartnerSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    terms_and_conditions = serializers.SerializerMethodField()
    location_address = serializers.SerializerMethodField()
    working_hours = serializers.SerializerMethodField()
    category_name = serializers.SerializerMethodField()
    category = CategorySerializer(read_only=True)
    logo = serializers.SerializerMethodField()
    photos = PartnerPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Partner
        fields = [
            'id', 'name', 'description', 'terms_and_conditions', 'category',
            'category_name', 'logo', 'photos', 'location_address', 'latitude',
            'longitude', 'offer_percentage', 'rating', 'review_count',
            'phone', 'website', 'working_hours', 'price_range'
        ]

    def get_name(self, obj):
        return get_translated(obj, 'name', self.context.get('request'))

    def get_description(self, obj):
        return get_translated(obj, 'description', self.context.get('request'))

    def get_terms_and_conditions(self, obj):
        return get_translated(obj, 'terms_and_conditions', self.context.get('request'))

    def get_location_address(self, obj):
        return get_translated(obj, 'location_address', self.context.get('request'))

    def get_working_hours(self, obj):
        return get_translated(obj, 'working_hours', self.context.get('request'))

    def get_category_name(self, obj):
        return get_translated(obj.category, 'name', self.context.get('request'))

    def get_logo(self, obj):
        request = self.context.get('request')
        if obj.logo:
            url = obj.logo.url
            if request:
                return request.build_absolute_uri(url)
            return url
        return None


class DiscountCouponSerializer(serializers.ModelSerializer):
    partner = PartnerSerializer(read_only=True)

    class Meta:
        model = DiscountCoupon
        fields = ['id', 'partner', 'code', 'discount_pct', 'status', 'valid_until', 'created_at']
