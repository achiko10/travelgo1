from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
import openai
import json

from .models import PointOfInterest, RedZone, CheckIn
from .serializers import POISerializer, RedZoneSerializer, CheckInRequestSerializer
from .utils import haversine_distance


# ─── Maps & Locations ──────────────────────────────────────────────────────────

class POIList(generics.ListAPIView):
    """
    GET /api/maps/pois/ — ყველა POI (ლოკაცია) სიის გამოტანა

    Optional Query Params:
      ?lat=41.69&lon=44.83&radius=500   → 500მ რადიუსში POI-ები
      ?poi_type=museum                  → ტიპის მიხედვით ფილტრი
    """
    serializer_class = POISerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = PointOfInterest.objects.all()

        # ── ტიპის ფილტრი ──────────────────────────────────────
        poi_type = self.request.query_params.get('poi_type')
        if poi_type:
            qs = qs.filter(poi_type=poi_type)

        # ── დისტანციის ფილტრი (Haversine + DB Bounding Box Pre-filter) ──
        try:
            lat    = float(self.request.query_params.get('lat'))
            lon    = float(self.request.query_params.get('lon'))
            radius = float(self.request.query_params.get('radius', 5000))  # default 5km
        except (TypeError, ValueError):
            return qs  # params-ი არ არის — ყველა POI ვაბრუნოთ

        # Bounding box pre-filter (~111km per degree latitude)
        lat_deg = radius / 111000.0
        lon_deg = radius / 85000.0  # Approx for Georgia latitude ~41-43deg
        qs = qs.filter(
            latitude__range=(lat - lat_deg, lat + lat_deg),
            longitude__range=(lon - lon_deg, lon + lon_deg)
        )

        nearby_ids = [
            poi.id for poi in qs
            if haversine_distance(lat, lon, poi.latitude, poi.longitude) <= radius
        ]
        return qs.filter(id__in=nearby_ids)


class RedZoneList(generics.ListAPIView):
    """GET /api/maps/redzones/ — Anti-Scam Red Zones კოორდინატებით"""
    queryset = RedZone.objects.all()
    serializer_class = RedZoneSerializer
    permission_classes = [permissions.AllowAny]


# ─── Check-In (Anti-Cheat) ─────────────────────────────────────────────────────

class PerformCheckIn(APIView):
    """POST /api/maps/checkin/ — Check-in + Haversine Anti-Cheat (40მ) + Drop System"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CheckInRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        poi_id   = serializer.validated_data['poi_id']
        user_lat = serializer.validated_data['user_lat']
        user_lon = serializer.validated_data['user_lon']

        poi = get_object_or_404(PointOfInterest, id=poi_id)

        # Anti-Cheat: Haversine — 40 მეტრის რადიუსი
        distance = haversine_distance(user_lat, user_lon, poi.latitude, poi.longitude)
        if distance > 40:
            return Response(
                {
                    "error": "თვალთმაქცობა! თქვენ არ იმყოფებით ლოკაციიდან 40 მეტრის რადიუსში.",
                    "current_distance_meters": int(distance)
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Duplicate Check-In
        if CheckIn.objects.filter(user=request.user, poi=poi).exists():
            return Response(
                {"error": "თქვენ უკვე აღმოაჩინეთ ეს ადგილი."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Anti-Cheat: Velocity Check (GPS Teleportation / Spoofing Check)
        last_checkin = CheckIn.objects.filter(user=request.user).order_by('-timestamp').first()
        if last_checkin:
            time_diff_seconds = (timezone.now() - last_checkin.timestamp).total_seconds()
            if time_diff_seconds > 0:
                dist_km = haversine_distance(
                    last_checkin.poi.latitude, last_checkin.poi.longitude,
                    poi.latitude, poi.longitude
                ) / 1000.0
                speed_kmh = (dist_km / time_diff_seconds) * 3600.0
                # თუ სიჩქარე 200 კმ/სთ-ზე მეტია (მაგ: 1 წუთში სხვა ქალაქში ტელეპორტირება)
                if speed_kmh > 200:
                    return Response(
                        {"error": "GPS Spoofing ეჭვი: გადაადგილების სიჩქარე რეალისტურ ზღვარს აჭარბებს."},
                        status=status.HTTP_400_BAD_REQUEST
                    )

        from django.db import transaction
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with transaction.atomic():
            # Check-In შექმნა
            CheckIn.objects.create(user=request.user, poi=poi, awarded_xp=poi.base_xp)

            # საპრიზო სისტემა: ბეჯი ან სკინი მომხმარებლის ინვენტარში
            from inventory.models import UserInventory
            dropped_item = None

            if poi.reward_badge and not UserInventory.objects.filter(user=request.user, badge=poi.reward_badge).exists():
                UserInventory.objects.create(
                    user=request.user, badge=poi.reward_badge,
                    location_unlocked_from=poi.name
                )
                dropped_item = {"type": "badge", "name": poi.reward_badge.name, "rarity": poi.reward_badge.rarity}
            elif poi.reward_skin and not UserInventory.objects.filter(user=request.user, skin=poi.reward_skin).exists():
                UserInventory.objects.create(
                    user=request.user, skin=poi.reward_skin,
                    location_unlocked_from=poi.name
                )
                dropped_item = {"type": "skin", "name": poi.reward_skin.name, "region": poi.reward_skin.region_unlock}

            # XP და Level განახლება (select_for_update)
            locked_user = User.objects.select_for_update().get(pk=request.user.pk)
            locked_user.xp += poi.base_xp
            
            # PvP ჩელენჯის (გამოწვევის) შემოწმება და დასრულება
            from social.models import ChallengeInvite
            from django.db.models import Q
            from django.utils import timezone
            
            active_challenge = ChallengeInvite.objects.filter(
                Q(from_user=locked_user) | Q(to_user=locked_user),
                poi=poi,
                status='accepted'
            ).first()
            
            challenge_bonus = 0
            if active_challenge:
                active_challenge.status = 'completed'
                active_challenge.winner = locked_user
                active_challenge.completed_at = timezone.now()
                active_challenge.save()
                
                challenge_bonus = active_challenge.bonus_xp
                locked_user.xp += challenge_bonus
            
            locked_user.level = locked_user.calculate_level()
            locked_user.save(update_fields=['xp', 'level'])

            # Daily Quests პროგრესის განახლება
            try:
                from quests.views import increment_user_quest_progress
                increment_user_quest_progress(user=request.user, target_poi=poi, count=1)
            except Exception as e:
                pass

        request.user.refresh_from_db()
        
        msg = "Check-in successful! Reward Claimed."
        if challenge_bonus > 0:
            msg = f"Check-in successful! You won the PvP Challenge and earned +{challenge_bonus} Bonus XP! 🏆"
        return Response({
            "message":              msg,
            "awarded_xp":           poi.base_xp,
            "new_total_xp":         request.user.xp,
            "new_level":            request.user.level,
            "dropped_item":         dropped_item or "No exclusive items dropped",
            "poi": {
                "id":   poi.id,
                "name": poi.name,
                "type": poi.get_poi_type_display(),
            }
        }, status=status.HTTP_200_OK)


# ─── AI Tour Planner ───────────────────────────────────────────────────────────

class AITourPlannerView(APIView):
    """POST /api/maps/ai-tour/ — OpenAI GPT-3.5 ტურის გეგმის გენერაცია JSON ფორმატში"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        interests = request.data.get('interests', 'sightseeing, local food')
        hours     = request.data.get('hours', 3)

        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == 'your_openai_api_key_here':
            # Smart dynamic planner fallback for Tbilisi
            stops = ["Rike Park & Bridge of Peace", "Narikala Fortress via Cable Car", "Old Tbilisi (Abanotubani) Sulfur Baths"]
            if "food" in interests.lower() or "wine" in interests.lower() or "eat" in interests.lower():
                stops = ["Shardeni Street Cafe Row", "Traditional Georgian Bakery (Tone)", "Wine Degustation in Sololaki", "Khachapuri at Machakhela"]
            elif "park" in interests.lower() or "nature" in interests.lower() or "view" in interests.lower():
                stops = ["Mtatsminda Park & Funicular", "Tbilisi National Botanical Garden", "Turtle Lake Panoramic Loop"]
            elif "history" in interests.lower() or "museum" in interests.lower() or "church" in interests.lower():
                stops = ["Sioni Cathedral & Anchiskhati", "Georgian National Museum", "Metekhi Church overlooking Kura"]

            # Limit stops based on hours requested
            max_stops = max(1, min(len(stops), int(hours)))
            selected_stops = stops[:max_stops]

            tour_data = {
                "tour_title": f"Tbilisi Express {interests.capitalize()} Tour",
                "description": f"A personalized {hours}-hour tour whitelisted for your interest in '{interests}'.",
                "stops": selected_stops
            }
            return Response(tour_data, status=status.HTTP_200_OK)

        openai.api_key = settings.OPENAI_API_KEY
        prompt = (
            f"I have {hours} hours free and my travel interests are: {interests}. "
            f"Create a short tailored travel itinerary for Tbilisi, Georgia. "
            f"Respond in JSON only with keys: 'tour_title', 'description', 'stops' (list of place names)."
        )

        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional Georgian travel planner returning JSON."},
                    {"role": "user",   "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            tour_data = json.loads(response.choices[0].message.content)
            return Response(tour_data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "AI failure: " + str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── AR Reward ─────────────────────────────────────────────────────────────────

class ARRewardView(APIView):
    """POST /api/maps/ar-reward/ — AR სკანირების ჯილდო (კოინები + XP)"""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        poi_id   = request.data.get('poi_id')
        user_lat = request.data.get('user_lat')
        user_lon = request.data.get('user_lon')

        if not poi_id:
            return Response(
                {"error": "poi_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        poi = get_object_or_404(PointOfInterest, id=poi_id)

        # Anti-Cheat: GPS proximity check (100მ რადიუსი AR-სთვის)
        if user_lat is not None and user_lon is not None:
            try:
                distance = haversine_distance(
                    float(user_lat), float(user_lon),
                    poi.latitude, poi.longitude
                )
                if distance > 100:
                    return Response(
                        {"error": "თქვენ ძალიან შორს ხართ AR ობიექტისგან.",
                         "current_distance_meters": int(distance)},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except (TypeError, ValueError):
                pass  # GPS მონაცემები არ მოვიდა — გამოტოვე ვალიდაცია

        # Anti-Cheat: ჩეკინის არსებობის შემოწმება — AR ჯილდო მხოლოდ ჩეკინის შემდეგ
        from maps.models import CheckIn
        if not CheckIn.objects.filter(user=request.user, poi=poi).exists():
            return Response(
                {"error": "ჯერ ჩეკინი გააკეთეთ ამ ლოკაციაზე AR ჯილდოს მისაღებად."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Daily limit: ერთ POI-ზე დღეში ერთხელ AR ჯილდო
        today = timezone.now().date()
        already_claimed = CheckIn.objects.filter(
            user=request.user,
            poi=poi,
            timestamp__date=today
        ).exists()
        # შენიშვნა: timestamp__date=today ამოწმებს დღევანდელ ჩეკინს AR ჯილდოს ლიმიტისთვის
        if already_claimed:
            return Response(
                {"error": "AR ჯილდო ამ ლოკაციაზე დღეს უკვე მიღებულია."},
                status=status.HTTP_400_BAD_REQUEST
            )

        from django.db import transaction
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # AR ჯილდოს ოდენობა
        ar_coins = 50
        ar_xp = 25

        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(pk=request.user.pk)
            locked_user.coins += ar_coins
            locked_user.xp += ar_xp
            locked_user.level = locked_user.calculate_level()
            locked_user.save(update_fields=['coins', 'xp', 'level'])

        request.user.refresh_from_db()

        return Response({
            "success": True,
            "message": f"AR Treasure collected! +{ar_coins} Coins, +{ar_xp} XP",
            "awarded_coins": ar_coins,
            "awarded_xp": ar_xp,
            "new_total_coins": request.user.coins,
            "new_total_xp": request.user.xp,
            "new_level": request.user.level,
        }, status=status.HTTP_200_OK)

