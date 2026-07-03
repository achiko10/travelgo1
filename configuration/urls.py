from django.urls import path
from .views import OnboardingSlideListView, SystemConfigView, AppTranslationView, ARTutorialStepListView

urlpatterns = [
    path('onboarding/', OnboardingSlideListView.as_view(), name='config-onboarding'),
    path('global/',     SystemConfigView.as_view(),        name='config-global'),
    path('translations/', AppTranslationView.as_view(),       name='config-translations'),
    path('ar-tutorial/', ARTutorialStepListView.as_view(),     name='config-ar-tutorial'),
]
