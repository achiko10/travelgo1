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


class MyCouponsView(APIView):
    """
    GET /api/partners/my-coupons/
    მომხმარებლის ყველა კუპონი + ნებისმიერი მომხმარებლისთვის გამიზნული
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        coupons = DiscountCoupon.objects.filter(
            status='active'
        ).filter(
            # ან ამ user-ისთვის, ან ყველასთვის (user=None)
            user__in=[request.user, None]
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

        # user შემოწმება — კუპონი სხვისი?
        if coupon.user and coupon.user != request.user:
            return Response(
                {"error": "ეს კუპონი სხვა მომხმარებლისთვისაა გამიზნული."},
                status=status.HTTP_403_FORBIDDEN
            )

        from django.utils import timezone
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
