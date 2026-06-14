from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LanguageViewSet

app_name = 'language'

router = DefaultRouter()
router.register(r'', LanguageViewSet, basename='language')

urlpatterns = [
    path('', include(router.urls)),
]
