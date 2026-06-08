"""Seed random open tasks for bishal@baniya.com.

Run from backend/:
  venv\\Scripts\\python.exe manage.py shell -c "exec(open('scripts/seed_bishal_tasks.py', encoding='utf-8').read())"
"""
from decimal import Decimal
import random

from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.tasks.models import Category, Task

User = get_user_model()
OWNER_EMAIL = "bishal@baniya.com"
COUNT = 18

TASK_TEMPLATES = [
    {
        "title": "Deep clean 2BHK apartment in Lazimpat",
        "description": "Need a thorough clean before guests arrive. Kitchen, bathrooms, and living room.",
        "category": "cleaning",
        "budget_range": (2500, 6000),
    },
    {
        "title": "Fix leaking kitchen tap in Baluwatar",
        "description": "Tap has been dripping for a week. Parts can be reimbursed if needed.",
        "category": "plumbing",
        "budget_range": (800, 2500),
    },
    {
        "title": "Help move sofa and wardrobe to new flat",
        "description": "Moving within Patan. Two heavy items, stairs involved. Truck not provided.",
        "category": "moving",
        "budget_range": (3000, 8000),
    },
    {
        "title": "Assemble IKEA desk and bookshelf",
        "description": "Two flat-pack items, tools available on site in Koteshwor.",
        "category": "assembly",
        "budget_range": (1500, 4000),
    },
    {
        "title": "Paint one bedroom wall accent color",
        "description": "Single accent wall, paint supplied. Prep and two coats in Budhanilkantha.",
        "category": "painting",
        "budget_range": (4000, 12000),
    },
    {
        "title": "Lawn trim and hedge shaping",
        "description": "Small garden maintenance in Bhaktapur. Green waste disposal included.",
        "category": "gardening",
        "budget_range": (1200, 3500),
    },
    {
        "title": "Deliver documents across Kathmandu Valley",
        "description": "Five stops with signatures required. Must have motorbike and valid license.",
        "category": "delivery",
        "budget_range": (1000, 3000),
    },
    {
        "title": "Install ceiling fan in living room",
        "description": "Fan purchased already. Wiring point exists in Sanepa.",
        "category": "handyman",
        "budget_range": (1500, 4500),
    },
    {
        "title": "Mount TV on brick wall",
        "description": "55-inch TV bracket supplied. Need stud finder and masonry drill in Thamel.",
        "category": "home-services",
        "budget_range": (1200, 3500),
    },
    {
        "title": "Weekly office cleaning — Sat morning",
        "description": "Small startup office in Pulchowk. Floors, desks, kitchenette.",
        "category": "cleaning",
        "budget_range": (2000, 5000),
    },
]

NEPAL_LOCATIONS = [
    ("Kathmandu", "Bagmati", Decimal("27.717200"), Decimal("85.324000")),
    ("Lalitpur", "Bagmati", Decimal("27.658800"), Decimal("85.324700")),
    ("Bhaktapur", "Bagmati", Decimal("27.671000"), Decimal("85.429800")),
    ("Pokhara", "Gandaki", Decimal("28.209600"), Decimal("83.985600")),
    ("Chitwan", "Bagmati", Decimal("27.529100"), Decimal("84.354200")),
    ("Butwal", "Lumbini", Decimal("27.700000"), Decimal("83.448300")),
]

TIME_LABELS = ["Morning", "Afternoon", "Evening", "Anytime", "Before 5 PM"]

owner = User.objects.filter(email__iexact=OWNER_EMAIL).first()
if not owner:
    raise SystemExit(f"User not found: {OWNER_EMAIL}")

categories = {c.slug: c for c in Category.objects.filter(is_active=True)}
created = 0
now = timezone.now()

for i in range(COUNT):
    template = random.choice(TASK_TEMPLATES)
    category = categories.get(template["category"]) or next(iter(categories.values()), None)
    city, state, lat, lng = random.choice(NEPAL_LOCATIONS)
    budget = Decimal(random.randint(template["budget_range"][0], template["budget_range"][1]))
    due_date = now + timedelta(days=random.randint(2, 21), hours=random.randint(8, 18))

    suffix = random.randint(100, 999)
    title = template["title"]
    if Task.objects.filter(owner=owner, title=title).exists():
        title = f"{title} ({suffix})"

    Task.objects.create(
        title=title,
        description=template["description"],
        category=category,
        owner=owner,
        status="open",
        work_type=random.choice(["in_person", "flexible", "remote"]),
        urgency=random.choice(["low", "medium", "high"]),
        budget_type="fixed",
        budget_amount=budget,
        budget_currency="NPR",
        location_type=random.choice(["physical", "physical", "remote"]),
        address=f"{random.choice(['Ward 3', 'Ward 7', 'Ward 12', 'Main Road'])}",
        city=city,
        state=state,
        country="Nepal",
        latitude=lat + Decimal(str(round(random.uniform(-0.02, 0.02), 6))),
        longitude=lng + Decimal(str(round(random.uniform(-0.02, 0.02), 6))),
        due_date=due_date,
        is_public=True,
        allow_bids=True,
        published_at=now,
        tags=[template["category"], city.lower()],
        requirements=[random.choice(TIME_LABELS)],
    )
    created += 1

print(f"Seeded {created} open public tasks for {owner.email}")
print(f"Total open public tasks for owner: {Task.objects.filter(owner=owner, status='open', is_public=True).count()}")
