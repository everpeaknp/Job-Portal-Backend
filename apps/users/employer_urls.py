"""Public employer profile routes."""
from django.urls import path

from .employer_views import (
    EmployerPublicDetailView,
    EmployerPublicJobsView,
    EmployerPublicListView,
    EmployerPublicProjectsView,
    EmployerPublicReviewsView,
)

app_name = 'employers'

# Use <str:slug> so usernames may include dots (e.g. john.doe). Django's <slug:> disallows ".".
urlpatterns = [
    path('', EmployerPublicListView.as_view(), name='employer-list'),
    path('<str:slug>/projects/', EmployerPublicProjectsView.as_view(), name='employer-projects'),
    path('<str:slug>/jobs/', EmployerPublicJobsView.as_view(), name='employer-jobs'),
    path('<str:slug>/reviews/', EmployerPublicReviewsView.as_view(), name='employer-reviews'),
    path('<str:slug>/', EmployerPublicDetailView.as_view(), name='employer-detail'),
]