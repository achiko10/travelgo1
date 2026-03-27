"""
URL configuration for travelgo_core project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Travel Go API Docs",
      default_version='v1',
      description="Interactive documentation for Flutter development",
      contact=openapi.Contact(email="developer@travelgo.ge"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Swagger API Documentation endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/maps/', include('maps.urls')),
    path('api/partners/', include('partners.urls')),
    path('api/quests/', include('quests.urls')),
    path('api/inventory/', include('inventory.urls')),
]
