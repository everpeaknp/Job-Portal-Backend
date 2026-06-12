"""Seed random marketplace job listings (listing:job) for demo accounts.

Run from backend/:
  venv\\Scripts\\python.exe manage.py shell -c "exec(open('scripts/seed_demo_jobs.py', encoding='utf-8').read())"
"""
from __future__ import annotations

import json
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.tasks.listing import with_listing_kind
from apps.tasks.models import Category, Task
from apps.users.employer_profile_service import get_or_create_employer_profile

User = get_user_model()

ACCOUNTS = (
    ("bishal@baniya.com", 14),
    ("userc@userc.userc", 10),
)

JOB_CATEGORIES = [
    "Design & Creative",
    "Development & IT",
    "Writing & Translation",
    "Digital Marketing",
    "Video & Animation",
    "Finance & Accounting",
]

JOB_TEMPLATES = [
    {
        "title": "Senior Frontend Developer (React/Next.js)",
        "description": "Build and maintain customer-facing dashboards. Work with design team on component library.",
        "category": "Development & IT",
        "skills": ["React", "TypeScript", "Next.js", "Tailwind CSS"],
        "budget_range": (80000, 150000),
        "type": "Full Time",
    },
    {
        "title": "UI/UX Designer for mobile fintech app",
        "description": "End-to-end flows for onboarding, KYC, and payments. Figma handoff required.",
        "category": "Design & Creative",
        "skills": ["Figma", "UI Design", "Prototyping", "Design systems"],
        "budget_range": (45000, 90000),
        "type": "Contract",
    },
    {
        "title": "Nepali–English content writer (blog & SEO)",
        "description": "12 articles per month for travel and lifestyle brand. Keyword briefs provided.",
        "category": "Writing & Translation",
        "skills": ["SEO writing", "Nepali", "English", "WordPress"],
        "budget_range": (15000, 35000),
        "type": "Fixed Price",
    },
    {
        "title": "Social media manager — Instagram & TikTok",
        "description": "Content calendar, short-form video edits, and community replies for local restaurant chain.",
        "category": "Digital Marketing",
        "skills": ["Instagram", "TikTok", "Canva", "Analytics"],
        "budget_range": (25000, 55000),
        "type": "Contract",
    },
    {
        "title": "Video editor for YouTube explainers",
        "description": "Edit 8–12 minute educational videos. Motion graphics templates supplied.",
        "category": "Video & Animation",
        "skills": ["Premiere Pro", "After Effects", "Color grading"],
        "budget_range": (12000, 28000),
        "type": "Hourly",
    },
    {
        "title": "Part-time bookkeeper (QuickBooks)",
        "description": "Monthly reconciliation, expense categorization, and VAT-ready reports.",
        "category": "Finance & Accounting",
        "skills": ["QuickBooks", "Bookkeeping", "Excel", "Nepal tax basics"],
        "budget_range": (20000, 40000),
        "type": "Hourly",
    },
    {
        "title": "WordPress developer for company site refresh",
        "description": "Migrate legacy theme to block editor. Performance and accessibility pass required.",
        "category": "Development & IT",
        "skills": ["WordPress", "PHP", "CSS", "Performance"],
        "budget_range": (35000, 75000),
        "type": "Fixed Price",
    },
    {
        "title": "Brand identity designer — logo & guidelines",
        "description": "Logo suite, colour palette, and one-page brand guide for café reopening.",
        "category": "Design & Creative",
        "skills": ["Branding", "Illustrator", "Logo design"],
        "budget_range": (18000, 42000),
        "type": "Fixed Price",
    },
    {
        "title": "Google Ads specialist (lead gen)",
        "description": "Set up and optimize search campaigns for property listings in Kathmandu Valley.",
        "category": "Digital Marketing",
        "skills": ["Google Ads", "Landing pages", "Conversion tracking"],
        "budget_range": (30000, 60000),
        "type": "Contract",
    },
    {
        "title": "Technical translator EN↔NE (software docs)",
        "description": "Translate API documentation and in-app strings. Glossaries provided.",
        "category": "Writing & Translation",
        "skills": ["Translation", "Technical writing", "English", "Nepali"],
        "budget_range": (10000, 22000),
        "type": "Fixed Price",
    },
    {
        "title": "Motion graphics for product launch reel",
        "description": "30–45 second hero video for SaaS launch. Script and VO supplied.",
        "category": "Video & Animation",
        "skills": ["After Effects", "Motion design", "Storyboarding"],
        "budget_range": (25000, 50000),
        "type": "Contract",
    },
    {
        "title": "Junior full-stack developer (Django + React)",
        "description": "Support feature work on marketplace platform. Code reviews and tests expected.",
        "category": "Development & IT",
        "skills": ["Django", "React", "PostgreSQL", "REST APIs"],
        "budget_range": (50000, 95000),
        "type": "Full Time",
    },
]

NEPAL_LOCATIONS = [
    ("Kathmandu", "Bagmati", Decimal("27.717200"), Decimal("85.324000")),
    ("Lalitpur", "Bagmati", Decimal("27.658800"), Decimal("85.324700")),
    ("Bhaktapur", "Bagmati", Decimal("27.671000"), Decimal("85.429800")),
    ("Pokhara", "Gandaki", Decimal("28.209600"), Decimal("83.985600")),
    ("Remote", "", None, None),
]

LOGO_BGS = [
    "bg-[#192338]",
    "bg-[#3f3ebd]",
    "bg-[#ff1a53]",
    "bg-[#ab004b]",
    "bg-[#0f766e]",
    "bg-[#1d4ed8]",
]

ICON_TYPES = ["wave", "face", "in", "clover"]
LOCATIONS = ["Remote", "Hybrid", "In-office"]
DURATIONS = ["1-5 Days", "5-10 Days", "10-20 Days", "20-30 Days", "30+ Days"]
LEVELS = ["Entry Level", "Intermediate", "Expert"]
EXPENSE = ["Inexpensive", "Intermediate", "Expensive"]
HOURS = ["20 hrs/week", "30 hrs/week", "40 hrs/week", "Flexible"]

# Map job display type to task budget_type
BUDGET_TYPE_MAP = {
    "Hourly": "hourly",
    "Full Time": "fixed",
    "Part Time": "hourly",
    "Fixed Price": "fixed",
    "Contract": "fixed",
}

CATEGORY_SLUG_FALLBACK = {
    "Design & Creative": "painting",
    "Development & IT": "assembly",
    "Writing & Translation": "delivery",
    "Digital Marketing": "gardening",
    "Video & Animation": "handyman",
    "Finance & Accounting": "plumbing",
}


def resolve_company_name(user) -> str:
    profile = getattr(user, "employer_profile", None)
    if profile is None:
        try:
            profile = get_or_create_employer_profile(user)
        except Exception:
            profile = None
    if profile and profile.company_name.strip():
        return profile.company_name.strip()
    full = user.get_full_name().strip()
    if full:
        return full
    return user.email.split("@")[0].replace(".", " ").title()


def build_job_requirements(
    *,
    category_label: str,
    company_name: str,
    template: dict,
    rng: random.Random,
    budget_min: int,
    budget_max: int,
) -> list:
    location = rng.choice(LOCATIONS)
    job_form = {
        "title": template["title"],
        "category": category_label,
        "companyName": company_name,
        "companyLogoBg": rng.choice(LOGO_BGS),
        "companyIconType": rng.choice(ICON_TYPES),
        "verified": rng.random() < 0.35,
        "location": location,
        "city": "" if location == "Remote" else rng.choice(["Kathmandu", "Lalitpur", "Bhaktapur", "Pokhara"]),
        "duration": rng.choice(DURATIONS),
        "type": template["type"],
        "experienceLevel": rng.choice(LEVELS),
        "budgetMin": str(budget_min),
        "budgetMax": str(budget_max),
        "expenseLevel": rng.choice(EXPENSE),
        "hoursLabel": rng.choice(HOURS),
        "postedLabel": rng.choice(["Posted today", "Posted 2 days ago", "Posted this week"]),
        "skills": template["skills"],
        "description": template["description"],
        "keyResponsibilities": rng.sample(
            [
                "Deliver milestones on agreed timeline",
                "Join weekly sync with product owner",
                "Document work and hand off cleanly",
                "Respond within one business day",
            ],
            k=rng.randint(2, 3),
        ),
        "workExperience": rng.sample(
            [
                "2+ years in a similar role",
                "Portfolio or published work required",
                "Experience with remote collaboration",
                "Nepal-based or overlapping timezone",
            ],
            k=rng.randint(1, 2),
        ),
        "status": "Active",
    }
    return [
        {
            "type": "dashboard_meta",
            "value": json.dumps(
                {"form": "job", "category": category_label, "jobForm": job_form},
                ensure_ascii=False,
            ),
        }
    ]


def seed_jobs_for_user(owner, count: int, rng: random.Random, categories: dict) -> int:
    company_name = resolve_company_name(owner)
    now = timezone.now()
    created = 0

    for _ in range(count):
        template = rng.choice(JOB_TEMPLATES)
        category_label = template["category"]
        slug = CATEGORY_SLUG_FALLBACK.get(category_label, "delivery")
        category = categories.get(slug) or next(iter(categories.values()), None)

        budget_min, budget_max = template["budget_range"]
        budget_min = rng.randint(budget_min, max(budget_min, budget_max - 5000))
        budget_max = rng.randint(max(budget_min, budget_min + 1000), budget_max)
        budget_amount = Decimal(budget_max)

        city, state, lat, lng = rng.choice(NEPAL_LOCATIONS)
        is_remote = city == "Remote"
        location_label = rng.choice(LOCATIONS)
        if location_label == "Remote":
            is_remote = True

        due_date = now + timedelta(days=rng.randint(14, 60), hours=rng.randint(9, 17))
        suffix = rng.randint(100, 999)
        title = template["title"]
        if Task.objects.filter(owner=owner, title=title).exists():
            title = f"{title} ({suffix})"

        skills_line = ", ".join(template["skills"])
        description = (
            f"{template['description']}\n\n"
            f"Skills: {skills_line}\n"
            f"Company: {company_name}"
        )

        task = Task.objects.create(
            title=title,
            description=description,
            category=category,
            owner=owner,
            status="open",
            work_type="remote" if is_remote else rng.choice(["remote", "flexible", "in_person"]),
            urgency=rng.choice(["low", "medium", "high"]),
            budget_type=BUDGET_TYPE_MAP.get(template["type"], "fixed"),
            budget_amount=budget_amount,
            budget_currency="NPR",
            location_type="remote" if is_remote else rng.choice(["remote", "physical"]),
            address="" if is_remote else rng.choice(["Ward 4", "Ward 8", "Ring Road", "Trade Tower"]),
            city="" if is_remote else city,
            state="" if is_remote else state,
            country="Nepal",
            latitude=None
            if is_remote or lat is None
            else lat + Decimal(str(round(rng.uniform(-0.02, 0.02), 6))),
            longitude=None
            if is_remote or lng is None
            else lng + Decimal(str(round(rng.uniform(-0.02, 0.02), 6))),
            due_date=due_date,
            is_public=True,
            allow_bids=True,
            published_at=now - timedelta(days=rng.randint(0, 10), hours=rng.randint(0, 12)),
            tags=with_listing_kind(
                [slug, (city.lower() if city else "remote"), category_label.lower().replace(" ", "-")],
                "job",
            ),
            requirements=build_job_requirements(
                category_label=category_label,
                company_name=company_name,
                template=template,
                rng=rng,
                budget_min=budget_min,
                budget_max=budget_max,
            ),
            bids_count=rng.randint(0, 4),
        )
        created += 1
        print(f"  + {owner.email}: [{task.slug}] {task.title[:55]}")

    return created


def main() -> None:
    categories = {c.slug: c for c in Category.objects.filter(is_active=True)}
    if not categories:
        raise SystemExit("No active categories. Run: python manage.py seed_tasks")

    total = 0
    for email, count in ACCOUNTS:
        owner = User.objects.filter(email__iexact=email).first()
        if not owner:
            print(f"SKIP — user not found: {email}")
            continue
        rng = random.Random(f"jobs-{email}")
        print(f"\nSeeding {count} jobs for {email} ({resolve_company_name(owner)})...")
        total += seed_jobs_for_user(owner, count, rng, categories)

    print(f"\nDone — seeded {total} job listings.")
    for email, _ in ACCOUNTS:
        owner = User.objects.filter(email__iexact=email).first()
        if not owner:
            continue
        n = Task.objects.filter(owner=owner, tags__icontains="listing:job").count()
        print(f"  {email}: {n} total job listings")


main()
