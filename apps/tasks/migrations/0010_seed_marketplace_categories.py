# Seed marketplace categories for task, job, project, and service listings.

import uuid

from django.db import migrations
from django.utils.text import slugify


TASK_CATEGORIES = [
    'Cleaning',
    'Delivery',
    'Handyman',
    'Gardening',
    'Home Services',
    'Moving',
    'Painting',
    'Plumbing',
    'Assembly',
    'IT Support',
    'Electrical',
    'Carpentry',
    'Repairs',
    'Pet Care',
    'Shopping',
    'Writing',
    'Photography',
    'Events',
    'Cooking',
    'Personal Assistant',
    'Business Support',
]

JOB_CATEGORIES = [
    'Design & Creative',
    'Development & IT',
    'Writing & Translation',
    'Digital Marketing',
    'Video & Animation',
    'Finance & Accounting',
    'Admin & Virtual Assistant',
    'Customer Service',
    'Sales & Business Development',
    'Legal & Compliance',
    'Engineering & Architecture',
    'HR & Recruiting',
    'Data Science & Analytics',
    'Product & Project Management',
]

PROJECT_CATEGORIES = [
    'Web Development',
    'Mobile Development',
    'Design & Creative',
    'Backend Development',
    'DevOps & Cloud',
    'Marketing',
    'Data & Analytics',
    'UI/UX Design',
    'E-commerce Development',
    'SaaS & Web Apps',
    'Content & Copywriting',
    'Branding & Identity',
]

SERVICE_CATEGORIES = [
    'Web & App Design',
    'Art & Illustration',
    'Design & Creative',
    'Development & IT',
    'Digital Marketing',
    'Video & Animation',
    'Logo Design & Branding',
    'SEO & SEM',
    'Social Media Marketing',
    'WordPress & CMS',
    'Translation & Localization',
    'Voice Over & Audio',
    '3D Modeling & Animation',
]

ALL_CATEGORY_SEEDS = (
    (TASK_CATEGORIES, 'task'),
    (JOB_CATEGORIES, 'job'),
    (PROJECT_CATEGORIES, 'project'),
    (SERVICE_CATEGORIES, 'service'),
)


def seed_all_categories(apps, schema_editor):
    Category = apps.get_model('tasks', 'Category')
    for names, listing_kind in ALL_CATEGORY_SEEDS:
        for order, name in enumerate(names):
            slug = slugify(name)[:100]
            Category.objects.get_or_create(
                name=name,
                listing_kind=listing_kind,
                defaults={
                    'id': uuid.uuid4(),
                    'slug': slug,
                    'order': order,
                    'is_active': True,
                },
            )


def unseed_all_categories(apps, schema_editor):
    Category = apps.get_model('tasks', 'Category')
    all_names_by_kind = [
        (TASK_CATEGORIES, 'task'),
        (JOB_CATEGORIES, 'job'),
        (PROJECT_CATEGORIES, 'project'),
        (SERVICE_CATEGORIES, 'service'),
    ]
    for names, listing_kind in all_names_by_kind:
        Category.objects.filter(listing_kind=listing_kind, name__in=names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_category_listing_kind'),
    ]

    operations = [
        migrations.RunPython(seed_all_categories, unseed_all_categories),
    ]
