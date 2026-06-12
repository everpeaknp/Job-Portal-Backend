"""Helpers for attaching placeholder cover images to marketplace services."""
from __future__ import annotations

import random
from typing import Iterable

from apps.tasks.models import TaskAttachment
from apps.tasks.listing import LISTING_KIND_SERVICE, get_listing_kind

# Curated Unsplash URLs — stable, hotlink-friendly service thumbnails.
SERVICE_COVER_IMAGES = [
    'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1626785774573-4b799315345d?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1551650975-87deedd944c3?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1498050108023-c5249f4df085?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1523474253048-8cd2745b5fd2?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1547658719-da2b51169166?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?auto=format&fit=crop&w=800&q=80',
    'https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?auto=format&fit=crop&w=800&q=80',
]


def pick_service_cover_url(service, *, rng: random.Random | None = None) -> str:
    """Return a deterministic-but-varied cover URL for a service."""
    randomizer = rng or random
    seed = str(getattr(service, 'pk', '') or getattr(service, 'id', '') or service.slug or service.title)
    if randomizer.random() < 0.35:
        return f'https://picsum.photos/seed/{seed}/800/600'
    index = abs(hash(seed)) % len(SERVICE_COVER_IMAGES)
    return SERVICE_COVER_IMAGES[index]


def service_has_cover_image(service) -> bool:
    return service.attachments.filter(file_type='image').exists()


def seed_service_cover_images(
    services: Iterable,
    *,
    only_missing: bool = True,
    images_per_service: int = 1,
    rng: random.Random | None = None,
) -> tuple[int, int]:
    """
    Attach random cover images to services.

    Returns (created_count, skipped_count).
    """
    randomizer = rng or random.Random()
    created = 0
    skipped = 0

    for service in services:
        if get_listing_kind(service.tags) != LISTING_KIND_SERVICE:
            skipped += 1
            continue

        if only_missing and service_has_cover_image(service):
            skipped += 1
            continue

        owner = service.owner
        if owner is None:
            skipped += 1
            continue

        for index in range(max(1, images_per_service)):
            file_url = pick_service_cover_url(service, rng=randomizer)
            if index:
                file_url = f'{file_url}&v={index}'

            TaskAttachment.objects.create(
                task=service,
                file_url=file_url,
                file_name=f'{service.slug or service.id}-cover-{index + 1}.jpg',
                file_type='image',
                file_size=randomizer.randint(120_000, 480_000),
                uploaded_by=owner,
            )
            created += 1

    return created, skipped
