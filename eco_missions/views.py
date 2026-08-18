from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from maps.utils import haversine_distance
from .models import Landmark, EcoMission, UserMissionProgress
from .serializers import LandmarkSerializer, EcoMissionSerializer, UserMissionProgressSerializer


class LandmarkListView(generics.ListAPIView):
    """GET /api/eco/landmarks/ — All landmarks."""
    queryset = Landmark.objects.all()
    serializer_class = LandmarkSerializer
    permission_classes = [permissions.AllowAny]


class EcoMissionListView(generics.ListAPIView):
    """GET /api/eco/missions/ — Active eco-missions."""
    serializer_class = EcoMissionSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        today = timezone.now().date()
        qs = EcoMission.objects.all()
        # Filter out expired campaign missions
        return qs.exclude(
            campaign_end_date__isnull=False,
            campaign_end_date__lt=today,
        )


class EcoMissionDetailView(generics.RetrieveAPIView):
    """GET /api/eco/missions/<id>/ — Mission detail."""
    queryset = EcoMission.objects.all()
    serializer_class = EcoMissionSerializer
    permission_classes = [permissions.AllowAny]


class StartMissionView(APIView):
    """
    POST /api/eco/missions/<id>/start/
    body: { "latitude": 41.7059, "longitude": 44.7546 }
    Starts a mission if user is within geofence.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        mission = get_object_or_404(EcoMission, pk=pk)

        # Check geofence
        user_lat = request.data.get('latitude')
        user_lon = request.data.get('longitude')

        if user_lat is not None and user_lon is not None and mission.geofence_radius_m:
            distance = haversine_distance(
                float(user_lat), float(user_lon),
                mission.latitude, mission.longitude,
            )
            if distance > mission.geofence_radius_m:
                return Response(
                    {"error": f"You are {int(distance)}m away. Must be within {mission.geofence_radius_m}m."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Create or get progress
        progress, created = UserMissionProgress.objects.get_or_create(
            user=request.user,
            mission=mission,
            defaults={'status': 'in_progress'},
        )
        if not created and progress.status == 'completed':
            return Response({"message": "Mission already completed."}, status=status.HTTP_200_OK)
        if not created:
            progress.status = 'in_progress'
            progress.save(update_fields=['status'])

        return Response({
            "success": True,
            "message": "Mission started!",
            "progress_id": progress.id,
            "requirements": mission.requirements,
            "buttons": mission.buttons,
        })


class CompleteMissionView(APIView):
    """
    POST /api/eco/missions/<id>/complete/
    Completes a mission and awards rewards.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        mission = get_object_or_404(EcoMission, pk=pk)
        progress = get_object_or_404(
            UserMissionProgress, user=request.user, mission=mission,
        )

        if progress.status == 'completed':
            return Response({"message": "Mission already completed."}, status=status.HTTP_200_OK)

        # Mark completed
        progress.status = 'completed'
        progress.completed_at = timezone.now()
        progress.xp_earned = mission.reward_xp
        progress.save()

        # Award user
        from django.db import transaction
        from django.contrib.auth import get_user_model
        User = get_user_model()

        with transaction.atomic():
            locked_user = User.objects.select_for_update().get(pk=request.user.pk)
            locked_user.xp += mission.reward_xp
            locked_user.coins += mission.reward_points
            locked_user.level = locked_user.calculate_level()
            locked_user.save(update_fields=['xp', 'coins', 'level'])

        request.user.refresh_from_db()

        return Response({
            "success": True,
            "message": "Mission completed!",
            "xp_earned": mission.reward_xp,
            "points_earned": mission.reward_points,
            "badge": mission.reward_badge,
            "skin": mission.reward_skin,
            "user_xp": request.user.xp,
            "user_coins": request.user.coins,
            "user_level": request.user.level,
        })


class MyMissionProgressView(generics.ListAPIView):
    """GET /api/eco/my-progress/ — User's mission progress."""
    serializer_class = UserMissionProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserMissionProgress.objects.filter(user=self.request.user)
