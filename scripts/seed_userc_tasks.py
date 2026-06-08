"""Seed random open tasks for userc@userc.userc.

Run from backend/:
  venv\\Scripts\\python.exe manage.py shell -c "exec(open('scripts/seed_userc_tasks.py', encoding='utf-8').read())"
"""
from decimal import Decimal
import random
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tasks.models import Category, Task

User = get_user_model()
OWNER_EMAIL = "userc@userc.userc"
COUNT = 18

TASK_TEMPLATES = [
    {
        "title": "End-of-lease apartment clean in Baneshwor",
        "description": "Full bond clean for a 1BHK. Oven, bathroom grout, and windows included.",
        "category": "cleaning",
        "budget_range": (2800, 6500),
    },
    {
        "title": "Unblock bathroom drain in Maharajgunj",
        "description": "Slow draining shower. Prefer someone with a snake or pressure tool.",
        "category": "plumbing",
        "budget_range": (900, 2800),
    },
    {
        "title": "Carry boxes from truck to 3rd floor",
        "description": "About 15 medium boxes, no elevator in Jawalakhel. Two-hour job.",
        "category": "moving",
        "budget_range": (1800, 4500),
    },
    {
        "title": "Build bunk bed for kids room",
        "description": "Flat-pack bunk bed, instructions included. Tools on site in Tokha.",
        "category": "assembly",
        "budget_range": (2000, 5000),
    },
    {
        "title": "Repaint front gate and fence",
        "description": "Metal gate needs rust treatment and two coats. Paint provided in Kirtipur.",
        "category": "painting",
        "budget_range": (3500, 9000),
    },
    {
        "title": "Trim overgrown hedge before monsoon",
        "description": "Front hedge roughly 8 metres. Clippings to be bagged in Gokarna.",
        "category": "gardening",
        "budget_range": (1500, 4000),
    },
    {
        "title": "Pick up and deliver pharmacy order",
        "description": "Collect prepaid medicines from Thapathali and deliver to Boudha same day.",
        "category": "delivery",
        "budget_range": (800, 2200),
    },
    {
        "title": "Replace broken door handle set",
        "description": "New handle set supplied. Need fitting on wooden door in Naxal.",
        "category": "handyman",
        "budget_range": (1000, 3000),
    },
    {
        "title": "Hang curtains and blinds in two rooms",
        "description": "Six curtain rods and two roller blinds. Ladder available in Chabahil.",
        "category": "home-services",
        "budget_range": (1400, 3800),
    },
    {
        "title": "Deep clean shared kitchen after renovation",
        "description": "Post-renovation dust on cabinets, floor, and appliances in Kalanki.",
        "category": "cleaning",
        "budget_range": (3200, 7000),
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

for _ in range(COUNT):
    template = random.choice(TASK_TEMPLATES)
    category = categories.get(template["category"]) or next(iter(categories.values()), None)
    city, state, lat, lng = random.choice(NEPAL_LOCATIONS)
    budget = Decimal(random.randint(template["budget_range"][0], template["budget_range"][1]))
    due_date = now + timedelta(days=random.randint(2, 21), hours=random.randint(8, 18))

    Task.objects.create(
        title=template["title"],
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
        address=random.choice(["Ward 3", "Ward 7", "Ward 12", "Main Road"]),
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
