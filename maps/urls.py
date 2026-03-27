from django.urls import path
from .views import POIList, RedZoneList, PerformCheckIn, AITourPlannerView

urlpatterns = [
    path('pois/', POIList.as_view(), name='poi_list'),
    path('redzones/', RedZoneList.as_view(), name='redzone_list'),
    path('checkin/', PerformCheckIn.as_view(), name='perform_checkin'),
    path('ai-tour/', AITourPlannerView.as_view(), name='ai_tour_planner'),
]
