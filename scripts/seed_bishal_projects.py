"""Seed random dashboard projects (listing:project) for bishal@baniya.com.

Run from backend/:
  python manage.py shell -c "exec(open('scripts/seed_bishal_projects.py', encoding='utf-8').read())"
"""
import json
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tasks.listing import with_listing_kind
from apps.tasks.models import Category, Task

User = get_user_model()
OWNER_EMAIL = "bishal@baniya.com"
COUNT = 16

PROJECT_TEMPLATES = [
    {
        "title": "Build company landing page in React",
        "description": "Need a responsive marketing site with contact form and CMS-ready sections.",
        "category": "assembly",
        "budget_range": (15000, 45000),
        "budget_type": "fixed",
    },
    {
        "title": "Logo and brand kit for café reopening",
        "description": "Logo, color palette, menu card layout, and social media templates.",
        "category": "painting",
        "budget_range": (8000, 20000),
        "budget_type": "fixed",
    },
    {
        "title": "Bookkeeping cleanup for Q1 FY 2082",
        "description": "Reconcile bank statements, categorize expenses, and prepare summary report.",
        "category": "delivery",
        "budget_range": (5000, 12000),
        "budget_type": "fixed",
    },
    {
        "title": "Product photo editing for e-commerce catalog",
        "description": "Background removal and color correction for 80 SKU images.",
        "category": "cleaning",
        "budget_range": (3000, 9000),
        "budget_type": "fixed",
    },
    {
        "title": "Mobile app UI redesign — Figma handoff",
        "description": "Redesign onboarding and checkout flows for an existing fintech app.",
        "category": "handyman",
        "budget_range": (25000, 60000),
        "budget_type": "fixed",
    },
    {
        "title": "SEO content writing — 12 blog posts",
        "description": "English articles for Nepal travel niche, 1200–1500 words each.",
        "category": "delivery",
        "budget_range": (12000, 24000),
        "budget_type": "fixed",
    },
    {
        "title": "Warehouse inventory audit support",
        "description": "On-site counting and spreadsheet entry over two weekends in Bhaktapur.",
        "category": "moving",
        "budget_range": (4000, 8000),
        "budget_type": "hourly",
    },
    {
        "title": "Nepali–English subtitle translation for training videos",
        "description": "Ten short L&D videos, SRT format, technical vocabulary provided.",
        "category": "delivery",
        "budget_range": (6000, 15000),
        "budget_type": "fixed",
    },
    {
        "title": "WordPress plugin bug fixes",
        "description": "Fix checkout and email notification issues on WooCommerce store.",
        "category": "plumbing",
        "budget_range": (10000, 25000),
        "budget_type": "fixed",
    },
    {
        "title": "Social media manager — 30-day campaign",
        "description": "Content calendar, post design, and engagement for local restaurant.",
        "category": "gardening",
        "budget_range": (8000, 18000),
        "budget_type": "fixed",
    },
]

NEPAL_LOCATIONS = [
    ("Kathmandu", "Bagmati", Decimal("27.717200"), Decimal("85.324000")),
    ("Lalitpur", "Bagmati", Decimal("27.658800"), Decimal("85.324700")),
    ("Bhaktapur", "Bagmati", Decimal("27.671000"), Decimal("85.429800")),
    ("Pokhara", "Gandaki", Decimal("28.209600"), Decimal("83.985600")),
    ("Remote", "", None, None),
]

STATUS_POOL = (
    ["open"] * 6
    + ["draft"] * 3
    + ["assigned", "in_progress", "funded"] * 1
    + ["completed"] * 2
    + ["cancelled"] * 2
)

CATEGORY_LABELS = {
    "assembly": "Assembly",
    "cleaning": "Cleaning",
    "delivery": "Delivery",
    "gardening": "Gardening",
    "handyman": "Handyman",
    "moving": "Moving",
    "painting": "Painting",
    "plumbing": "Plumbing",
}


def dashboard_meta(category_slug: str) -> list:
    label = CATEGORY_LABELS.get(category_slug, category_slug.title())
    return [
        {
            "type": "dashboard_meta",
            "value": json.dumps({"form": "project", "category": label}),
        }
    ]


owner = User.objects.filter(email__iexact=OWNER_EMAIL).first()
if not owner:
    raise SystemExit(f"User not found: {OWNER_EMAIL}")

tasker = (
    User.objects.filter(role="tasker", is_active=True).exclude(pk=owner.pk).first()
    or User.objects.filter(is_active=True).exclude(pk=owner.pk).first()
)

categories = {c.slug: c for c in Category.objects.filter(is_active=True)}
if not categories:
    raise SystemExit("No active categories found. Run seed_tasks or create categories first.")

random.shuffle(STATUS_POOL)
now = timezone.now()
created = 0

for i in range(COUNT):
    template = random.choice(PROJECT_TEMPLATES)
    category = categories.get(template["category"]) or next(iter(categories.values()))
    category_slug = category.slug if category else template["category"]
    city, state, lat, lng = random.choice(NEPAL_LOCATIONS)
    is_remote = city == "Remote"
    budget = Decimal(random.randint(template["budget_range"][0], template["budget_range"][1]))
    due_date = now + timedelta(days=random.randint(3, 45), hours=random.randint(9, 17))
    status = STATUS_POOL[i] if i < len(STATUS_POOL) else "open"

    suffix = random.randint(100, 999)
    title = template["title"]
    if Task.objects.filter(owner=owner, title=title).exists():
        title = f"{title} ({suffix})"

    assigned_tasker = None
    if status in {"assigned", "in_progress", "funded", "completed"} and tasker:
        assigned_tasker = tasker

    task = Task.objects.create(
        title=title,
        description=template["description"],
        category=category,
        owner=owner,
        assigned_tasker=assigned_tasker,
        status=status,
        work_type="remote" if is_remote else random.choice(["in_person", "flexible", "remote"]),
        urgency=random.choice(["low", "medium", "high"]),
        budget_type=template["budget_type"],
        budget_amount=budget,
        budget_currency="NPR",
        location_type="remote" if is_remote else random.choice(["physical", "remote"]),
        address="" if is_remote else random.choice(["Ward 5", "Ward 9", "Ring Road", "Main Chowk"]),
        city="" if is_remote else city,
        state="" if is_remote else state,
        country="Nepal",
        latitude=None if is_remote or lat is None else lat + Decimal(str(round(random.uniform(-0.02, 0.02), 6))),
        longitude=None if is_remote or lng is None else lng + Decimal(str(round(random.uniform(-0.02, 0.02), 6))),
        due_date=due_date,
        is_public=status not in {"draft", "cancelled"},
        allow_bids=status in {"open", "draft"},
        published_at=now if status != "draft" else None,
        tags=with_listing_kind([category_slug, city.lower() if city else "remote"], "project"),
        requirements=dashboard_meta(category_slug),
        bids_count=random.randint(0, 5) if status == "open" else 0,
        completed_at=now - timedelta(days=random.randint(1, 14)) if status == "completed" else None,
        cancelled_at=now - timedelta(days=random.randint(1, 7)) if status == "cancelled" else None,
    )
    created += 1
    print(f"  + [{status}] {task.slug} — {task.title[:50]}")

print(f"\nSeeded {created} projects for {owner.email}")
print(
    f"Total project listings: "
    f"{Task.objects.filter(owner=owner, tags__icontains='listing:project').count()}"
)
