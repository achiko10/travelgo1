from rest_framework import generics, permissions
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
