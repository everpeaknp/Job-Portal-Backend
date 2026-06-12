"""Attach random cover images to marketplace services."""
from django.core.management.base import BaseCommand

from apps.services.models import Service
from apps.services.service_image_seed import seed_service_cover_images


class Command(BaseCommand):
    help = 'Seed random cover images for services (TaskAttachment rows).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--replace',
            action='store_true',
            help='Add images even when a service already has a cover image.',
        )
        parser.add_argument(
            '--count',
            type=int,
            default=1,
            help='Number of images to attach per service (default: 1).',
        )

    def handle(self, *args, **options):
        only_missing = not options['replace']
        images_per_service = max(1, options['count'])

        services = Service.objects.select_related('owner').prefetch_related('attachments')
        created, skipped = seed_service_cover_images(
            services,
            only_missing=only_missing,
            images_per_service=images_per_service,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Done — {created} image(s) created, {skipped} service(s) skipped.'
            )
        )
