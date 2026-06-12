"""Public freelancer profile routes."""
from django.urls import path

from .freelancer_views import (
    FreelancerPublicDetailView,
    FreelancerPublicPortfolioView,
    FreelancerPublicReviewsView,
    FreelancerPublicServicesView,
)

app_name = 'freelancers'

urlpatterns = [
    path('<str:slug>/reviews/', FreelancerPublicReviewsView.as_view(), name='freelancer-reviews'),
    path('<str:slug>/portfolio/', FreelancerPublicPortfolioView.as_view(), name='freelancer-portfolio'),
    path('<str:slug>/services/', FreelancerPublicServicesView.as_view(), name='freelancer-services'),
    path('<str:slug>/', FreelancerPublicDetailView.as_view(), name='freelancer-detail'),
]
