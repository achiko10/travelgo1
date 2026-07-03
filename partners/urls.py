from django.urls import path
from .views import CategoryList, PartnerList, MyCouponsView, RedeemCouponView

urlpatterns = [
    path('categories/', CategoryList.as_view(),    name='category-list'),
    path('list/',       PartnerList.as_view(),      name='partner-list'),
    path('my-coupons/', MyCouponsView.as_view(),    name='my-coupons'),
    path('redeem/',     RedeemCouponView.as_view(), name='redeem-coupon'),
]
