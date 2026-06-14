# Nepal-context marketplace categories (local services, tourism, NGO, etc.).

import uuid

from django.db import migrations
from django.utils.text import slugify


NEPAL_TASK_CATEGORIES = [
    'Home Shifting & Moving',
    'Mason & Construction',
    'Whitewashing & Painting',
    'AC Repair & Servicing',
    'Appliance Repair',
    'Motorcycle & Vehicle Repair',
    'CCTV & Security Installation',
    'Solar Panel Installation',
    'Water Tank Cleaning',
    'Carpet & Sofa Cleaning',
    'Tailoring & Alterations',
    'Grocery & Parcel Delivery',
    'Tutoring & Home Lessons',
    'Nepali-English Translation',
    'Wedding & Event Help',
    'Puja & Ritual Setup',
    'Cooking & Catering Help',
    'Labour & Load Carrying',
    'Babysitting & Eldercare',
    'Interior Decoration',
    'Welding & Fabrication',
    'Pest Control',
    'Load & Unload Help',
    'Generator & Inverter Repair',
    'Roofing & Waterproofing',
]

NEPAL_JOB_CATEGORIES = [
    'Tourism & Hospitality',
    'NGO & Development',
    'Agriculture & Agribusiness',
    'Construction & Civil Engineering',
    'Healthcare & Nursing',
    'Education & Training',
    'Local Language & Translation',
    'Accounting & Tax (Nepal)',
    'Real Estate & Property',
    'Import Export & Logistics',
    'Renewable Energy & Solar',
    'Hotel & Restaurant Management',
    'Banking & Microfinance',
    'Media & Journalism',
]

NEPAL_PROJECT_CATEGORIES = [
    'Tourism & Travel Website',
    'E-commerce for Nepali Business',
    'Restaurant & Hotel Booking System',
    'School & College Management System',
    'Local Business Branding',
    'Nepali Content & Copywriting',
    'Payment Gateway Integration',
    'GIS & Mapping Solutions',
    'NGO Project Management System',
    'Mobile App for Local Services',
    'Inventory & Billing Software',
    'Community & Membership Portal',
]

NEPAL_SERVICE_CATEGORIES = [
    'Nepali Translation & Localization',
    'Tax Filing & Accounting (Nepal)',
    'CV, SOP & Resume Writing',
    'Tour Package Content Writing',
    'Social Media for Local Shops',
    'Menu & Signboard Design',
    'Wedding Invitation Design',
    'NGO Proposal & Report Writing',
    'SEO for Nepal Market',
    'Product & Food Photography',
    'YouTube Video Editing',
    'Voice Over (Nepali & English)',
    'Handwritten & Digital Invitations',
    'Business Registration Support',
]

NEPAL_CATEGORY_SEEDS = (
    (NEPAL_TASK_CATEGORIES, 'task'),
    (NEPAL_JOB_CATEGORIES, 'job'),
    (NEPAL_PROJECT_CATEGORIES, 'project'),
    (NEPAL_SERVICE_CATEGORIES, 'service'),
)

JUNK_CATEGORY_NAMES = ['ssss', 'deswd']


def seed_nepal_categories(apps, schema_editor):
    Category = apps.get_model('tasks', 'Category')
    Category.objects.filter(name__in=JUNK_CATEGORY_NAMES).delete()

    for names, listing_kind in NEPAL_CATEGORY_SEEDS:
        base_order = Category.objects.filter(listing_kind=listing_kind).count()
        for offset, name in enumerate(names):
            slug = slugify(name.strip())[:100]
            Category.objects.get_or_create(
                name=name.strip(),
                listing_kind=listing_kind,
                defaults={
                    'id': uuid.uuid4(),
                    'slug': slug,
                    'order': base_order + offset,
                    'is_active': True,
                },
            )


def unseed_nepal_categories(apps, schema_editor):
    Category = apps.get_model('tasks', 'Category')
    for names, listing_kind in NEPAL_CATEGORY_SEEDS:
        Category.objects.filter(
            listing_kind=listing_kind,
            name__in=[n.strip() for n in names],
        ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0010_seed_marketplace_categories'),
    ]

    operations = [
        migrations.RunPython(seed_nepal_categories, unseed_nepal_categories),
    ]
