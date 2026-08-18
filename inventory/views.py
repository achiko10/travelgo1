from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from .models import Badge, Skin, UserInventory
from .serializers import BadgeSerializer, SkinSerializer, UserInventorySerializer

class AvailableBadgesList(generics.ListAPIView):
    """ GET list of all possible distinct badges in the gamified system """
    queryset = Badge.objects.all()
    serializer_class = BadgeSerializer
    permission_classes = [permissions.AllowAny]

class AvailableSkinsList(generics.ListAPIView):
    """ GET list of all possible geographical skins """
    queryset = Skin.objects.all()
    serializer_class = SkinSerializer
    permission_classes = [permissions.AllowAny]

class MyInventory(generics.ListAPIView):
    """ GET current authenticated user's strictly owned backpack items """
    serializer_class = UserInventorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserInventory.objects.filter(user=self.request.user)


class PurchaseItem(APIView):
    """ POST /api/inventory/purchase/ — Purchase item using coins safely """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        item_name = request.data.get('item_name')
        if not item_name:
            return Response({"error": "Item name is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Check if item is skin or badge
        skin = Skin.objects.filter(name=item_name, is_for_sale=True).first()
        badge = Badge.objects.filter(name=item_name, is_for_sale=True).first()

        if not skin and not badge:
            return Response({"error": "Item not found or not for sale"}, status=status.HTTP_404_NOT_FOUND)

        price = skin.coin_price if skin else badge.coin_price

        # Transaction atomic block to prevent concurrent transaction race conditions
        try:
            with transaction.atomic():
                user = request.user
                # Force refresh user from DB with write lock
                user_refresh = user.__class__.objects.select_for_update().get(id=user.id)

                if user_refresh.coins < price:
                    return Response({"error": "Insufficient coins balance"}, status=status.HTTP_400_BAD_REQUEST)

                # Check if already owned
                if skin:
                    already_owned = UserInventory.objects.filter(user=user_refresh, skin=skin).exists()
                elif badge:
                    already_owned = UserInventory.objects.filter(user=user_refresh, badge=badge).exists()
                else:
                    already_owned = False

                if already_owned:
                    return Response({"error": "Item already purchased"}, status=status.HTTP_400_BAD_REQUEST)

                # Deduct coins and save
                user_refresh.coins -= price
                user_refresh.save()

                # Add to inventory
                UserInventory.objects.create(
                    user=user_refresh,
                    skin=skin,
                    badge=badge
                )

                return Response({"message": "Purchase completed successfully", "new_balance": user_refresh.coins})
        except Exception as e:
            return Response({"error": "Transaction failed. Please try again."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
