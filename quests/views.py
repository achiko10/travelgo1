from rest_framework import generics, permissions
from django.utils import timezone
from .models import DailyQuest, UserQuestProgress
from .serializers import DailyQuestSerializer, UserQuestProgressSerializer

class ActiveQuestsList(generics.ListAPIView):
    """
    Returns only the quests that are generated for today.
    """
    serializer_class = DailyQuestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return DailyQuest.objects.filter(date_active=timezone.now().date())

class MyQuestProgress(generics.ListAPIView):
    serializer_class = UserQuestProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserQuestProgress.objects.filter(user=self.request.user)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import QuizQuestion, UserQuizSubmission, UserPuzzleSubmission

from .serializers import QuizQuestionSerializer
from maps.models import PointOfInterest
from django.db import transaction

class QuizView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        poi_id = request.query_params.get('poi_id')
        if not poi_id:
            return Response({"error": "poi_id parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        questions = QuizQuestion.objects.filter(poi_id=poi_id)
        serializer = QuizQuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data)


class QuizSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        poi_id = request.data.get('poi_id')
        score = request.data.get('score', 0)
        
        if not poi_id:
            return Response({"error": "poi_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        poi = get_object_or_404(PointOfInterest, id=poi_id)
        user = request.user
        
        # Check if already submitted today to prevent double rewards
        already_submitted = UserQuizSubmission.objects.filter(user=user, poi=poi).exists()
        if already_submitted:
            return Response({"message": "Quiz already submitted for this location today"}, status=status.HTTP_200_OK)
            
        with transaction.atomic():
            UserQuizSubmission.objects.create(user=user, poi=poi, score=score)
            
            # Award rewards: 15 coins and 100 XP
            user.coins += 15
            user.xp += 100
            user.save()
            
        return Response({
            "success": True,
            "coins": user.coins,
            "xp": user.xp
        }, status=status.HTTP_200_OK)


class PuzzleSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        poi_id = request.data.get('poi_id')
        
        if not poi_id:
            return Response({"error": "poi_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        poi = get_object_or_404(PointOfInterest, id=poi_id)
        user = request.user
        
        # Check if already submitted today to prevent double rewards
        already_submitted = UserPuzzleSubmission.objects.filter(user=user, poi=poi).exists()
        if already_submitted:
            return Response({"message": "Puzzle already solved for this location today"}, status=status.HTTP_200_OK)
            
        with transaction.atomic():
            UserPuzzleSubmission.objects.create(user=user, poi=poi)
            
            # Award rewards: 25 coins and 150 XP
            user.coins += 25
            user.xp += 150
            user.save()
            
        return Response({
            "success": True,
            "coins": user.coins,
            "xp": user.xp
        }, status=status.HTTP_200_OK)

