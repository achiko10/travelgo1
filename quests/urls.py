from django.urls import path
from .views import ActiveQuestsList, MyQuestProgress, QuizView, QuizSubmitView, PuzzleSubmitView, ClaimQuestRewardView

urlpatterns = [
    path('daily/', ActiveQuestsList.as_view(), name='daily_quests'),
    path('my-progress/', MyQuestProgress.as_view(), name='my_quests'),
    path('claim/', ClaimQuestRewardView.as_view(), name='claim_quest'),
    path('quiz/', QuizView.as_view(), name='quiz_get'),
    path('quiz/submit/', QuizSubmitView.as_view(), name='quiz_submit'),
    path('puzzle/submit/', PuzzleSubmitView.as_view(), name='puzzle_submit'),
]

