from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

from .models import DailyQuest, UserQuestProgress, QuizQuestion, UserQuizSubmission, UserPuzzleSubmission
from .serializers import DailyQuestSerializer, UserQuestProgressSerializer, QuizQuestionSerializer
from maps.models import PointOfInterest

User = get_user_model()

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


def increment_user_quest_progress(user, target_poi=None, count=1):
    """
    ავტომატურად უმატებს პროგრესს მომხმარებლის აქტიურ ქვესთებს
    (მაგ. Check-in-ის, ქვიზის ან ეკო მისიის შესრულებისას).
    """
    from django.db.models import Q
    today = timezone.now().date()
    active_quests = DailyQuest.objects.filter(Q(date_active=today) | Q(date_active__isnull=True))
    
    if target_poi:
        active_quests = active_quests.filter(Q(target_poi=target_poi) | Q(target_poi__isnull=True))
    else:
        active_quests = active_quests.filter(target_poi__isnull=True)

    for quest in active_quests:
        progress_obj, _ = UserQuestProgress.objects.get_or_create(user=user, quest=quest)
        if not progress_obj.is_completed:
            progress_obj.progress += count
            if progress_obj.progress >= quest.required_checkins:
                progress_obj.progress = quest.required_checkins
                progress_obj.is_completed = True
            progress_obj.save()


class ClaimQuestRewardView(APIView):
    """
    POST /api/quests/claim/
    Request Body: {"quest_id": 1}
    ჯილდოს (XP/Coins) დარიცხვა დასრულებული ქვესთისთვის.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        quest_id = request.data.get('quest_id')
        if not quest_id:
            return Response({"error": "quest_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        quest = get_object_or_404(DailyQuest, id=quest_id)
        progress_obj = get_object_or_404(UserQuestProgress, user=request.user, quest=quest)

        if not progress_obj.is_completed:
            return Response({"error": "ქვესთი ჯერ არ არის დასრულებული"}, status=status.HTTP_400_BAD_REQUEST)

        if progress_obj.is_claimed:
            return Response({"message": "პრიზი უკვე აღებული გაქვთ"}, status=status.HTTP_200_OK)

        with transaction.atomic():
            progress_obj.is_claimed = True
            progress_obj.save(update_fields=['is_claimed'])

            locked_user = User.objects.select_for_update().get(pk=request.user.pk)
            locked_user.xp += quest.reward_xp
            locked_user.coins += quest.reward_coins
            locked_user.level = locked_user.calculate_level()
            locked_user.save(update_fields=['xp', 'coins', 'level'])

        return Response({
            "success": True,
            "reward_xp": quest.reward_xp,
            "reward_coins": quest.reward_coins,
            "total_xp": locked_user.xp,
            "total_coins": locked_user.coins,
            "level": locked_user.level
        }, status=status.HTTP_200_OK)


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

            # Daily Quests პროგრესის განახლება
            try:
                increment_user_quest_progress(user=user, target_poi=poi, count=1)
            except Exception:
                pass
            
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

