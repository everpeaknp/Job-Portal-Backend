"""Bookmark URL configuration."""
from django.urls import path

from .views import BookmarkListAPIView, BookmarkToggleAPIView

urlpatterns = [
    path('', BookmarkListAPIView.as_view(), name='bookmark-list'),
    path('<slug:slug>/', BookmarkToggleAPIView.as_view(), name='bookmark-toggle'),
]
