from celery import shared_task
from django.utils import timezone
from .models import Banner

@shared_task
def update_banner_status_task():
    """
    Task to update the is_active field of banners based on end_time.
    """
    now = timezone.now()
    expired_banners = Banner.objects.filter(end_time__lte=now, is_active=True)
    expired_banners.update(is_active=False)