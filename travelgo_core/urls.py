"""
URL configuration for travelgo_core project.
"""
from django.contrib import admin
from django.urls import path, include, re_path

# ━━━ Admin Panel Branding ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
admin.site.site_header  = "🗺️ TravelGo — ადმინ პანელი"
admin.site.site_title   = "TravelGo Admin"
admin.site.index_title  = "მართვის პანელი"
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from django.conf import settings

schema_view = get_schema_view(
   openapi.Info(
      title="Travel Go API Docs",
      default_version='v1',
      description="Interactive documentation for Flutter development",
      contact=openapi.Contact(email="developer@travelgo.ge"),
   ),
   public=settings.DEBUG,
   permission_classes=(permissions.AllowAny if settings.DEBUG else permissions.IsAdminUser,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger API Documentation endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # API endpoints
    path('api/users/',     include('users.urls')),
    path('api/maps/',      include('maps.urls')),
    path('api/partners/',  include('partners.urls')),
    path('api/quests/',    include('quests.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/config/',    include('configuration.urls')),
    path('api/social/',    include('social.urls')),
    path('api/eco/',       include('eco_missions.urls')),
]
