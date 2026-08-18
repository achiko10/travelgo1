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
        from django.db.models import Q
        today = timezone.now().date()
        return DailyQuest.objects.filter(Q(date_active=today) | Q(date_active__isnull=True))

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
from django.contrib.auth import get_user_model

User = get_user_model()

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
        user_answers = request.data.get('answers') # e.g. {"question_id": selected_index}
        
        if not poi_id:
            return Response({"error": "poi_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        poi = get_object_or_404(PointOfInterest, id=poi_id)
        
        # Calculate score on backend if answers array/dict provided
        if user_answers and isinstance(user_answers, dict):
            questions = QuizQuestion.objects.filter(poi=poi)
            calculated_score = 0
            for q in questions:
                selected = user_answers.get(str(q.id))
                if selected is not None and int(selected) == q.correct_index:
                    calculated_score += 1
            score = calculated_score
        else:
            # Fallback: cap client-sent score to maximum 10
            raw_score = request.data.get('score', 0)
            score = min(max(0, int(raw_score)), 10)
            
        user = request.user
        
        # დღიური ლიმიტის შემოწმება — მხოლოდ დღევანდელი თარიღით
        today = timezone.now().date()
        already_submitted = UserQuizSubmission.objects.filter(
            user=user, poi=poi, date_submitted__date=today
        ).exists()
        if already_submitted:
            return Response({"message": "ქვიზი ამ ლოკაციაზე დღეს უკვე გაკეთებულია"}, status=status.HTTP_200_OK)
            
        with transaction.atomic():
            UserQuizSubmission.objects.create(user=user, poi=poi, score=score)
            
            # select_for_update() — race condition-ის დაცვა
            locked_user = User.objects.select_for_update().get(pk=user.pk)
            locked_user.coins += 15
            locked_user.xp += 100
            locked_user.level = locked_user.calculate_level()
            locked_user.save(update_fields=['coins', 'xp', 'level'])
            
        user.refresh_from_db()
        return Response({
            "success": True,
            "coins": user.coins,
            "xp": user.xp,
            "level": user.level
        }, status=status.HTTP_200_OK)


class PuzzleSubmitView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        poi_id = request.data.get('poi_id')
        
        if not poi_id:
            return Response({"error": "poi_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
        poi = get_object_or_404(PointOfInterest, id=poi_id)
        user = request.user
        
        # დღიური ლიმიტის შემოწმება — მხოლოდ დღევანდელი თარიღით
        today = timezone.now().date()
        already_submitted = UserPuzzleSubmission.objects.filter(
            user=user, poi=poi, date_submitted__date=today
        ).exists()
        if already_submitted:
            return Response({"message": "პაზლი ამ ლოკაციაზე დღეს უკვე გაკეთებულია"}, status=status.HTTP_200_OK)
            
        with transaction.atomic():
            UserPuzzleSubmission.objects.create(user=user, poi=poi)
            
            # select_for_update() — race condition-ის დაცვა
            locked_user = User.objects.select_for_update().get(pk=user.pk)
            locked_user.coins += 25
            locked_user.xp += 150
            locked_user.level = locked_user.calculate_level()
            locked_user.save(update_fields=['coins', 'xp', 'level'])
            
        user.refresh_from_db()
        return Response({
            "success": True,
            "coins": user.coins,
            "xp": user.xp,
            "level": user.level
        }, status=status.HTTP_200_OK)

