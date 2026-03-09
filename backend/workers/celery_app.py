"""
Celery Application Configuration
"""
import os
from celery import Celery
from celery.schedules import crontab


# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Create Celery app
app = Celery('real_estate_workers')

# Configure Celery
app.conf.update(
    broker_url=os.getenv('CELERY_BROKER_URL',
                         'amqp://guest:guest@localhost:5672//'),
    result_backend=os.getenv('CELERY_RESULT_BACKEND',
                             'redis://localhost:6379/0'),
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
)

# Auto-discover tasks
app.autodiscover_tasks(['workers.tasks'])

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Update property embeddings daily
    'update-property-embeddings': {
        'task': 'workers.tasks.embedding_tasks.update_all_property_embeddings',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    # Refresh recommendations daily
    'refresh-recommendations': {
        'task': 'workers.tasks.recommendation_tasks.refresh_all_recommendations',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
    # Clean up old notifications weekly
    'cleanup-old-notifications': {
        'task': 'workers.tasks.notification_tasks.cleanup_old_notifications',
        # Weekly on Sunday
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
    },
    # Generate market analytics daily
    'generate-market-analytics': {
        'task': 'workers.tasks.ai_tasks.generate_market_analytics',
        'schedule': crontab(hour=5, minute=0),  # Daily at 5 AM
    },
}


@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery"""
    print(f'Request: {self.request!r}')
