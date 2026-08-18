from django.urls import path
from .views import (
    LandmarkListView,
    EcoMissionListView,
    EcoMissionDetailView,
    StartMissionView,
    CompleteMissionView,
    MyMissionProgressView,
)

urlpatterns = [
    path('landmarks/', LandmarkListView.as_view(), name='landmark-list'),
    path('missions/', EcoMissionListView.as_view(), name='eco-mission-list'),
    path('missions/<int:pk>/', EcoMissionDetailView.as_view(), name='eco-mission-detail'),
    path('missions/<int:pk>/start/', StartMissionView.as_view(), name='eco-mission-start'),
    path('missions/<int:pk>/complete/', CompleteMissionView.as_view(), name='eco-mission-complete'),
    path('my-progress/', MyMissionProgressView.as_view(), name='eco-my-progress'),
]
