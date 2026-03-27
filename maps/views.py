from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
import openai
import json

from .models import PointOfInterest, RedZone, CheckIn
from .serializers import POISerializer, RedZoneSerializer, CheckInRequestSerializer
from .utils import haversine_distance


# ─── Maps & Locations ──────────────────────────────────────────────────────────

class POIList(generics.ListAPIView):
    """GET /api/maps/pois/ — ყველა Point of Interest (ლოკაცია) სიის გამოტანა"""
    queryset = PointOfInterest.objects.all()
    serializer_class = POISerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class RedZoneList(generics.ListAPIView):
    """GET /api/maps/redzones/ — თაღლითების ზონები (Red Zones) კოორდინატებით"""
    queryset = RedZone.objects.all()
    serializer_class = RedZoneSerializer
    permission_classes = [permissions.AllowAny]


# ─── Check-In (Anti-Cheat) ─────────────────────────────────────────────────────

class PerformCheckIn(APIView):
    """POST /api/maps/checkin/ — Check-in + Haversine Anti-Cheat (40მ რადიუსი) + Drop System"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckInRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        poi_id = serializer.validated_data['poi_id']
        user_lat = serializer.validated_data['user_lat']
        user_lon = serializer.validated_data['user_lon']

        poi = get_object_or_404(PointOfInterest, id=poi_id)

        # Anti-Cheat: Haversine ფორმულა — 40 მეტრის რადიუსი
        distance = haversine_distance(user_lat, user_lon, poi.latitude, poi.longitude)
        if distance > 40:
            return Response(
                {
                    "error": "თვალთმაქცობა! თქვენ არ იმყოფებით ლოკაციიდან 40 მეტრის რადიუსში.",
                    "current_distance": int(distance)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Duplicate Check-In
        if CheckIn.objects.filter(user=request.user, poi=poi).exists():
            return Response({"error": "თქვენ უკვე აღმოაჩინეთ ეს ადგილი."}, status=status.HTTP_400_BAD_REQUEST)

        # Check-In შექმნა
        CheckIn.objects.create(user=request.user, poi=poi, awarded_xp=poi.base_xp)

        # Drop System: Badge ან Skin ინვენტარში
        from inventory.models import Badge, Skin, UserInventory
        dropped_item = None
        if poi.reward_badge_name:
            badge = Badge.objects.filter(name__iexact=poi.reward_badge_name).first()
            skin = Skin.objects.filter(name__iexact=poi.reward_badge_name).first()

            if badge and not UserInventory.objects.filter(user=request.user, badge=badge).exists():
                UserInventory.objects.create(user=request.user, badge=badge, location_unlocked_from=poi.name)
                dropped_item = f"Badge: {badge.name}"
            elif skin and not UserInventory.objects.filter(user=request.user, skin=skin).exists():
                UserInventory.objects.create(user=request.user, skin=skin, location_unlocked_from=poi.name)
                dropped_item = f"Skin: {skin.name}"

        # XP და Level განახლება
        user = request.user
        user.xp += poi.base_xp
        user.level = (user.xp // 100) + 1
        user.save()

        return Response({
            "message": "Check-in successful! Reward Claimed.",
            "awarded_xp": poi.base_xp,
            "new_total_xp": user.xp,
            "new_level": user.level,
            "dropped_item_in_backpack": dropped_item or "No new exclusive items dropped"
        }, status=status.HTTP_200_OK)


# ─── AI Tour Planner ───────────────────────────────────────────────────────────

class AITourPlannerView(APIView):
    """POST /api/maps/ai-tour/ — OpenAI GPT-3.5 ტურის გეგმის გენერაცია JSON ფორმატში"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        interests = request.data.get('interests', 'sightseeing, local food')
        hours = request.data.get('hours', 3)

        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your_openai_api_key_here':
            return Response(
                {"error": "OpenAI API Key is missing on the server. Add OPENAI_API_KEY to .env"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        openai.api_key = settings.OPENAI_API_KEY
        prompt = (
            f"I have {hours} hours free and my travel interests are: {interests}. "
            f"Create a short tailored travel itinerary. "
            f"Respond in JSON format only with keys: 'tour_title', 'description', 'stops' (list of place names)."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional travel planner returning JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            tour_data = json.loads(response.choices[0].message.content)
            return Response(tour_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "AI failure: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
