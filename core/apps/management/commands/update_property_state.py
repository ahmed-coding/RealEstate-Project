from django.core.management.base import BaseCommand
from django.utils import timezone
from ...models import Property
from django.db.models import Q


class Command(BaseCommand):
    def handle(self, *args, **options):

        property = Property.objects.filter(
            Q(last_active__lte=timezone.now()), is_active=True).update(is_active=False)

        print(property)

        # file = io.open(f'{settings.BASE_DIR}/log.txt', 'a')
        # file.write(f"{timezone.now()}\t-updated banners={banner}\n")
        # print(banner)
