"""Seed random employer + freelancer dashboard profile data for demo accounts.

Run from backend/:
  venv\\Scripts\\python.exe manage.py shell -c "exec(open('scripts/seed_demo_profiles.py', encoding='utf-8').read())"
"""
from __future__ import annotations

import json
import random
import uuid
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.users.badge_catalog import BADGE_CATALOG
from apps.users.employer_profile_service import get_or_create_employer_profile
from apps.users.models import UserBadge, UserSkill

User = get_user_model()

EMPLOYER_EMAIL = "bishal@baniya.com"
FREELANCER_EMAIL = "userc@userc.userc"

META_PREFIX = "META::"
EDU_PREFIX = "EDU::"
EXP_PREFIX = "EXP::"
AWD_PREFIX = "AWD::"
META_PROFILE_ID = "profile"

DASHBOARD_TO_API_TRANSPORT = {
    "Walking": "Walk",
    "Bicycle": "Bicycle",
    "Car": "Car",
    "Scooter": "Scooter",
    "Truck": "Truck",
    "Online": "Online",
}

LANGUAGE_LEVELS = {
    "Basic": "beginner",
    "Conversational": "intermediate",
    "Fluent": "expert",
    "Native / Bilingual": "expert",
}


def _encode(prefix: str, entry_id: str, category: str, payload: dict) -> dict:
    return {
        "name": f"{prefix}{entry_id}",
        "details": json.dumps(payload, ensure_ascii=False),
        "category": category,
        "proficiency_level": "intermediate",
    }


def _seed_id() -> str:
    return uuid.uuid4().hex[:12]


def _clear_skills(user) -> None:
    UserSkill.objects.filter(user=user).delete()


def _add_skill(user, **kwargs) -> None:
    UserSkill.objects.create(user=user, years_of_experience=0, verified=False, **kwargs)


def _upsert_badge(user, badge_type: str, *, verified: bool = True, document_number: str = "") -> None:
    name, description = BADGE_CATALOG[badge_type]
    badge, _created = UserBadge.objects.update_or_create(
        user=user,
        badge_type=badge_type,
        defaults={
            "name": name,
            "description": description,
            "is_verified": verified,
            "verified_at": timezone.now() if verified else None,
            "document_number": document_number,
        },
    )
    if verified and not badge.verified_at:
        badge.verified_at = timezone.now()
        badge.is_verified = True
        badge.save(update_fields=["verified_at", "is_verified"])


def seed_freelancer_profile(user, rng: random.Random) -> None:
    first_names = ["Suman", "Rita", "Anil", "Priya", "Kiran"]
    last_names = ["Shrestha", "Gurung", "Tamang", "Karki", "Maharjan"]
    cities = ["Kathmandu", "Lalitpur", "Bhaktapur", "Pokhara", "Biratnagar"]
    specializations = [
        "Electrical & wiring",
        "Plumbing & drainage",
        "Home cleaning",
        "Furniture assembly",
        "Gardening & landscaping",
        "Moving & delivery",
    ]
    profile_types = ["Individual", "Business", "Agency"]
    work_modes = ["location", "hybrid", "remote"]

    user.first_name = user.first_name or rng.choice(first_names)
    user.last_name = user.last_name or rng.choice(last_names)
    user.role = "tasker"
    user.tagline = rng.choice(
        [
            "Reliable handyman across Kathmandu Valley",
            "Licensed trades · On-time · Fair rates",
            "Quality work, clear communication",
            "Nepal-based freelancer · Flexible schedule",
        ]
    )
    user.bio = rng.choice(
        [
            "I help homeowners and small businesses with repairs, installs, and seasonal maintenance. "
            "I bring my own tools, share photos before/after, and keep quotes transparent.",
            "Experienced tasker with 5+ years serving Lalitpur and Kathmandu. I specialise in quick turnarounds "
            "and tidy finishes — no job too small.",
            "Practical problem-solver for plumbing, electrical basics, and general handyman work. "
            "Available mornings and weekends.",
        ]
    )
    user.city = rng.choice(cities)
    user.state = "Bagmati"
    user.country = "Nepal"
    user.phone = user.phone or f"98{rng.randint(10000000, 99999999)}"
    user.hourly_rate = Decimal(str(rng.choice([450, 600, 750, 900, 1200])))
    user.response_time = rng.choice([15, 30, 45, 60])
    user.completion_rate = Decimal(str(rng.choice([88, 92, 95, 97, 99])))
    user.tasks_completed = rng.randint(12, 84)
    user.average_rating = Decimal(str(round(rng.uniform(4.2, 4.9), 2)))
    user.total_reviews = rng.randint(5, 40)
    user.is_verified_tasker = True
    user.email_verified = True
    user.phone_verified = True
    if not user.username:
        user.username = user.email.split("@")[0]
    user.save()

    _clear_skills(user)

    specialization = rng.choice(specializations)
    profile_type = rng.choice(profile_types)
    work_mode = rng.choice(work_modes)

    meta = _encode(
        META_PREFIX,
        META_PROFILE_ID,
        "qualification",
        {
            "specialization": specialization,
            "profileType": profile_type,
            "workLocationMode": work_mode,
        },
    )
    _add_skill(user, **meta)

    education_templates = [
        ("2016 – 2019", "Diploma in Electrical Engineering", "CTEVT Polytechnic, Lalitpur"),
        ("2012 – 2015", "Certificate in Plumbing", "Nepal Technical Institute"),
        ("2018 – 2021", "Bachelor in Civil Engineering", "Pulchowk Campus"),
    ]
    for year_range, degree, institution in rng.sample(education_templates, k=rng.randint(1, 2)):
        entry = _encode(
            EDU_PREFIX,
            _seed_id(),
            "qualification",
            {
                "yearRange": year_range,
                "degree": degree,
                "institution": institution,
                "description": "Relevant coursework and practical labs.",
            },
        )
        _add_skill(user, **entry)

    experience_templates = [
        ("2021 – Present", "Lead Handyman", "Baniya Home Services", "Residential repairs and small renovations."),
        ("2018 – 2021", "Electrician Assistant", "Valley Electric Co.", "Wiring, panel upgrades, safety checks."),
        ("2019 – 2022", "Freelance Cleaner", "Self-employed", "Deep cleans and move-out services."),
    ]
    for year_range, title, company, description in rng.sample(experience_templates, k=rng.randint(2, 3)):
        entry = _encode(
            EXP_PREFIX,
            _seed_id(),
            "experience",
            {
                "yearRange": year_range,
                "title": title,
                "company": company,
                "description": description,
            },
        )
        _add_skill(user, **entry)

    award_templates = [
        ("2023", "Top Rated Tasker", "Airtasker Nepal", "Maintained 4.8+ rating over 20 jobs."),
        ("2022", "Safety Excellence", "Local Contractors Assoc.", "Zero incident record on site work."),
    ]
    for year_range, title, issuer, description in rng.sample(award_templates, k=1):
        entry = _encode(
            AWD_PREFIX,
            _seed_id(),
            "qualification",
            {
                "yearRange": year_range,
                "title": title,
                "issuer": issuer,
                "description": description,
            },
        )
        _add_skill(user, **entry)

    skill_names = [
        "Pipe fitting",
        "Circuit troubleshooting",
        "Furniture assembly",
        "Pressure washing",
        "Tile grouting",
        "Appliance install",
        "Garden pruning",
        "Load & unload",
    ]
    for skill_name in rng.sample(skill_names, k=rng.randint(4, 6)):
        _add_skill(
            user,
            name=skill_name,
            category="skill",
            proficiency_level=rng.choice(["beginner", "intermediate", "expert"]),
        )

    for transport_id in rng.sample(list(DASHBOARD_TO_API_TRANSPORT.keys()), k=rng.randint(2, 4)):
        _add_skill(
            user,
            name=DASHBOARD_TO_API_TRANSPORT[transport_id],
            category="transport",
            proficiency_level="intermediate",
        )

    language_pairs = [
        ("Nepali", "Native / Bilingual"),
        ("English", "Fluent"),
        ("Hindi", "Conversational"),
    ]
    for language, level in rng.sample(language_pairs, k=rng.randint(2, 3)):
        _add_skill(
            user,
            name=language,
            category="language",
            proficiency_level=LANGUAGE_LEVELS[level],
        )

    for badge_type in ("mobile_verified", "payment_verified", "police_check"):
        _upsert_badge(user, badge_type, verified=True)

    licence_choices = ["electrical_licence", "plumbing_licence"]
    for badge_type in rng.sample(licence_choices, k=rng.randint(1, 2)):
        _upsert_badge(
            user,
            badge_type,
            verified=True,
            document_number=f"LIC-{rng.randint(10000, 99999)}",
        )

    custom_name = rng.choice(
        ["First Aid Certificate", "Working at Heights", "Tool Safety Certification"]
    )
    UserBadge.objects.update_or_create(
        user=user,
        badge_type="custom_licence",
        name=custom_name,
        defaults={
            "description": BADGE_CATALOG["custom_licence"][1],
            "is_verified": True,
            "verified_at": timezone.now(),
            "document_number": f"badge:custom-{_seed_id()}|CERT-{rng.randint(1000, 9999)}",
        },
    )

    print(f"Freelancer profile seeded for {user.email} ({user.get_full_name()})")
    print(f"  Skills: {UserSkill.objects.filter(user=user).count()}, badges: {UserBadge.objects.filter(user=user).count()}")


def seed_employer_profile(user, rng: random.Random) -> None:
    user.role = "customer"
    user.first_name = user.first_name or "Bishal"
    user.last_name = user.last_name or "Baniya"
    user.tagline = rng.choice(
        [
            "Growing businesses across Nepal",
            "Hiring trusted local talent",
            "Property & facilities projects",
        ]
    )
    user.bio = rng.choice(
        [
            "We post regular home maintenance and renovation work across Kathmandu Valley. "
            "Clear briefs, fair budgets, and respectful communication.",
            "Small business owner looking for reliable freelancers for cleaning, repairs, and seasonal projects.",
            "Employer account for residential and light commercial tasks — fast decisions and on-time payment.",
        ]
    )
    user.city = rng.choice(["Kathmandu", "Lalitpur", "Bhaktapur"])
    user.state = "Bagmati"
    user.country = "Nepal"
    user.phone = user.phone or f"98{rng.randint(10000000, 99999999)}"
    user.tasks_posted = rng.randint(8, 45)
    user.email_verified = True
    if not user.username:
        user.username = "bishal"
    user.save()

    profile = get_or_create_employer_profile(user)
    profile.account_type = rng.choice(["individual", "company"])
    profile.company_name = rng.choice(
        [
            "Baniya Properties",
            "Baniya Ventures Pvt. Ltd.",
            "Bishal Home Projects",
            "Baniya Facilities",
        ]
    )
    profile.industry = rng.choice(
        ["Real Estate", "Hospitality", "Retail", "Construction", "Technology"]
    )
    profile.team_size = rng.choice(["Just me", "2–10", "11–50", "51–200"])
    profile.website = rng.choice(
        ["", "https://baniya.example.com", "https://bishal-homes.example.np"]
    )
    profile.cost_range = rng.choice(
        ["NPR 5k – 25k per task", "NPR 25k – 100k per project", "Flexible / quote based"]
    )
    profile.contact_email = user.email
    profile.contact_phone = user.phone or ""
    profile.logo_color = rng.choice(["serif-m", "sans-b", "mono-k", "rounded-g"])
    profile.logo_text = "".join(part[0] for part in profile.company_name.split()[:2]).upper()[:8] or "BB"
    profile.is_public = True
    profile.save()

    print(f"Employer profile seeded for {user.email} ({profile.company_name})")


def main() -> None:
    employer = User.objects.filter(email__iexact=EMPLOYER_EMAIL).first()
    freelancer = User.objects.filter(email__iexact=FREELANCER_EMAIL).first()
    if not employer:
        raise SystemExit(f"User not found: {EMPLOYER_EMAIL}")
    if not freelancer:
        raise SystemExit(f"User not found: {FREELANCER_EMAIL}")

    rng_employer = random.Random(employer.email)
    rng_freelancer = random.Random(freelancer.email)

    seed_employer_profile(employer, rng_employer)
    seed_freelancer_profile(freelancer, rng_freelancer)

    print("Done — refresh /dashboard/profile and employer business profile in the browser.")


main()
