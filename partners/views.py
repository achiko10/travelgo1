from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Category, Partner, DiscountCoupon
from .serializers import CategorySerializer, PartnerSerializer, DiscountCouponSerializer


class CategoryList(generics.ListAPIView):
    """GET /api/partners/categories/ — პარტნიორის კატეგორიების სია"""
    queryset         = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class PartnerList(generics.ListAPIView):
    """
    GET /api/partners/list/ — პარტნიორების სია
    Optional: ?category=1  — კატეგორიის მიხედვით ფილტრი
    """
    serializer_class   = PartnerSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs       = Partner.objects.all()
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category__id=category)
        return qs


from django.db.models import Q
from django.utils import timezone


class MyCouponsView(APIView):
    """
    GET /api/partners/my-coupons/
    მომხმარებლის ყველა კუპონი + ნებისმიერი მომხმარებლისთვის გამიზნული
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        today = timezone.now().date()
        # Auto-expire outdated coupons
        DiscountCoupon.objects.filter(
            status='active',
            valid_until__isnull=False,
            valid_until__lt=today
        ).update(status='expired')

        coupons = DiscountCoupon.objects.filter(
            status='active'
        ).filter(
            Q(user=request.user) | Q(user__isnull=True)
        ).select_related('partner', 'partner__category')

        serializer = DiscountCouponSerializer(coupons, many=True, context={'request': request})
        return Response({"coupons": serializer.data, "total": len(serializer.data)})



class RedeemCouponView(APIView):
    """
    POST /api/partners/redeem/
    body: { "code": "TBS-ABCD12" }
    კუპონის გამოყენება — status 'used'-ად გადადის
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        code = request.data.get('code', '').strip().upper()
        if not code:
            return Response({"error": "კოდი ცარიელია"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = DiscountCoupon.objects.get(code=code, status='active')
        except DiscountCoupon.DoesNotExist:
            return Response(
                {"error": "კუპონი ვერ მოიძებნა ან უკვე გამოყენებულია."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # H4 FIX: Check valid_until expiry date
        today = timezone.now().date()
        if coupon.valid_until and coupon.valid_until < today:
            coupon.status = 'expired'
            coupon.save(update_fields=['status'])
            return Response(
                {"error": "კუპონის ვარგისიანობის ვადა ამოწურულია."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # user შემოწმება — კუპონი სხვისი?
        if coupon.user and coupon.user != request.user:
            return Response(
                {"error": "ეს კუპონი სხვა მომხმარებლისთვისაა გამიზნული."},
                status=status.HTTP_403_FORBIDDEN
            )

        coupon.status  = 'used'
        coupon.user    = request.user
        coupon.used_at = timezone.now()
        coupon.save()

        return Response({
            "message":      f"🎉 კუპონი გამოყენებულია! {coupon.discount_pct}% ფასდაკლება.",
            "partner":      coupon.partner.name,
            "discount_pct": coupon.discount_pct,
            "address":      coupon.partner.location_address,
        })
