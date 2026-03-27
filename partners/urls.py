from django.urls import path
from .views import CategoryList, PartnerList

urlpatterns = [
    path('categories/', CategoryList.as_view(), name='category-list'),
    path('list/', PartnerList.as_view(), name='partner-list'),
]
