from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import OnboardingSlide, SystemConfig, AppTranslation, ARTutorialStep
from .serializers import OnboardingSlideSerializer, SystemConfigSerializer, ARTutorialStepSerializer
from travelgo_core.translation_utils import get_language

class OnboardingSlideListView(generics.ListAPIView):
    """GET /api/config/onboarding/ — ონბორდინგ სლაიდების სია (ავტორიზაციის გარეშე)"""
    queryset = OnboardingSlide.objects.filter(is_active=True)
    serializer_class = OnboardingSlideSerializer
    permission_classes = [permissions.AllowAny]


class SystemConfigView(APIView):
    """GET /api/config/global/ — აპლიკაციის გლობალური პარამეტრები (ავტორიზაციის გარეშე)"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        config = SystemConfig.objects.first()
        if not config:
            config = SystemConfig.objects.create()
        serializer = SystemConfigSerializer(config, context={'request': request})
        return Response(serializer.data)


class AppTranslationView(APIView):
    """GET /api/config/translations/ — ყველა UI ტექსტური თარგმანის Key-Value პასუხი"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        lang = get_language(request)
        translations = AppTranslation.objects.all()
        data = {}
        for t in translations:
            data[t.key] = t.text_en if lang == 'en' else t.text_ka
        return Response(data)


class ARTutorialStepListView(generics.ListAPIView):
    """GET /api/config/ar-tutorial/ — AR ტუტორიალის ნაბიჯები"""
    queryset = ARTutorialStep.objects.filter(is_active=True)
    serializer_class = ARTutorialStepSerializer
    permission_classes = [permissions.AllowAny]
