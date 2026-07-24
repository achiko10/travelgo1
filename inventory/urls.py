from django.urls import path
from .views import AvailableBadgesList, AvailableSkinsList, MyInventory, PurchaseItem

urlpatterns = [
    path('badges/', AvailableBadgesList.as_view(), name='badges'),
    path('skins/', AvailableSkinsList.as_view(), name='skins'),
    path('my-backpack/', MyInventory.as_view(), name='my_inventory'),
    path('purchase/', PurchaseItem.as_view(), name='purchase_item'),
]
