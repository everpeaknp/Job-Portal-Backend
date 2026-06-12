"""Seed verified bidirectional reviews for demo employer / freelancer / service pages.

Run from backend/:
  venv\\Scripts\\python.exe manage.py shell -c "exec(open('scripts/seed_demo_reviews.py', encoding='utf-8').read())"
"""
from __future__ import annotations

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.reviews.models import Review
from apps.reviews.services import ReviewService
from apps.services.models import Service
from apps.tasks.listing import (
    LISTING_KIND_SERVICE,
    filter_queryset_by_listing_kind,
    with_listing_kind,
)
from apps.tasks.models import Category, Task

User = get_user_model()

EMPLOYER_EMAIL = "bishal@baniya.com"
FREELANCER_EMAIL = "userc@userc.userc"

def _get_users():
    employer = User.objects.filter(email__iexact=EMPLOYER_EMAIL).first()
    freelancer = User.objects.filter(email__iexact=FREELANCER_EMAIL).first()
    if not employer:
        raise SystemExit(f"Employer not found: {EMPLOYER_EMAIL}")
    if not freelancer:
        raise SystemExit(f"Freelancer not found: {FREELANCER_EMAIL}")
    return employer, freelancer


def _ensure_completed_task(
    *,
    owner,
    tasker,
    title: str,
    tags: list | None = None,
) -> Task:
    task = (
        Task.objects.filter(
            owner=owner,
            assigned_tasker=tasker,
            title=title,
            status="completed",
        )
        .order_by("-completed_at", "-updated_at")
        .first()
    )
    if task:
        return task

    category = Category.objects.filter(is_active=True).first()
    now = timezone.now()
    task = Task.objects.create(
        title=title,
        description="Demo completed work for review seeding.",
        category=category,
        owner=owner,
        assigned_tasker=tasker,
        status="completed",
        work_type="remote",
        urgency="medium",
        budget_type="fixed",
        budget_amount=Decimal("5000.00"),
        budget_currency="NPR",
        location_type="remote",
        country="Nepal",
        is_public=True,
        allow_bids=False,
        published_at=now,
        completed_at=now,
        tags=tags or [],
    )
    return task


def _seed_reviews_for_task(task: Task, *, customer, tasker) -> int:
    ReviewService.send_review_invitations(task)
    created = 0

    pairs = (
        (customer, 5, "Clear brief and fair client. Would work together again.", ["friendly"]),
        (tasker, 4, "Solid delivery and good communication throughout.", ["professional"]),
    )
    for reviewer, rating, comment, tags in pairs:
        if Review.objects.filter(task=task, reviewer=reviewer).exists():
            continue
        ReviewService.create_review(
            task_id=task.id,
            reviewer=reviewer,
            rating=rating,
            comment=comment,
            tags=tags,
        )
        created += 1
        print(f"  + review by {reviewer.email} on task {task.slug}")

    return created


def _seed_service_listing_reviews(freelancer, customer) -> int:
    service = (
        filter_queryset_by_listing_kind(
            Service.objects.filter(owner=freelancer, status__in=["open", "completed"]),
            LISTING_KIND_SERVICE,
        )
        .order_by("-created_at")
        .first()
    )
    if not service:
        category = Category.objects.filter(is_active=True).first()
        now = timezone.now()
        service = Service.objects.create(
            title="Professional logo design package",
            description="Demo marketplace service for review seeding.",
            category=category,
            owner=freelancer,
            status="completed",
            work_type="remote",
            urgency="low",
            budget_type="fixed",
            budget_amount=Decimal("8000.00"),
            budget_currency="NPR",
            location_type="remote",
            country="Nepal",
            is_public=True,
            allow_bids=False,
            published_at=now,
            completed_at=now,
            tags=with_listing_kind(["design", "branding"], LISTING_KIND_SERVICE),
        )
        print(f"  + created demo service {service.slug}")

    if service.status != "completed" or service.assigned_tasker_id != customer.id:
        service.status = "completed"
        service.assigned_tasker = customer
        service.completed_at = service.completed_at or timezone.now()
        service.save(update_fields=["status", "assigned_tasker", "completed_at", "updated_at"])

    return _seed_reviews_for_task(service, customer=service.owner, tasker=customer)


def main() -> None:
    employer, freelancer = _get_users()
    created = 0

    general_task = _ensure_completed_task(
        owner=employer,
        tasker=freelancer,
        title="Demo completed project — review seed",
        tags=with_listing_kind(["demo"], "project"),
    )
    created += _seed_reviews_for_task(general_task, customer=employer, tasker=freelancer)

    reverse_task = _ensure_completed_task(
        owner=freelancer,
        tasker=employer,
        title="Demo completed gig — review seed",
    )
    created += _seed_reviews_for_task(reverse_task, customer=freelancer, tasker=employer)

    created += _seed_service_listing_reviews(freelancer, employer)

    ReviewService.update_user_profile_stats(employer)
    ReviewService.update_user_profile_stats(freelancer)

    print(f"\nSeeded {created} new review(s).")
    print(f"Employer {employer.email}: {employer.total_reviews} reviews, avg {employer.average_rating}")
    print(f"Freelancer {freelancer.email}: {freelancer.total_reviews} reviews, avg {freelancer.average_rating}")


main()
