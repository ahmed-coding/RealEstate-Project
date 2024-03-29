from typing import Any
from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Banner
from django.db.models import Q

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        
        banner = Banner.objects.filter(Q(end_time__lte=timezone.now())).update(is_active=False)
        
        print(banner)
        
        