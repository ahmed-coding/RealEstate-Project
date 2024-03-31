from typing import Any
from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Banner
from django.db.models import Q
import io
from django.conf import settings


class Command(BaseCommand):
    def handle(self, *args, **options):

        banner = Banner.objects.filter(
            Q(end_time__lte=timezone.now()), is_active=True).update(is_active=False)
        file = io.open(f'{settings.BASE_DIR}/log.txt', 'a')
        file.write(f"{timezone.now()}\t-updated banners={banner}\n")
        # print(banner)
