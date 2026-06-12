from django.urls import path

from .views import FaqListAPIView

app_name = 'faq'

urlpatterns = [
    path('', FaqListAPIView.as_view(), name='list'),
]
