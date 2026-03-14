from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from apps.models import Banner, User
from apps.utils import calculate_timestamp


class UtilsTestCase(TestCase):
    """Test utility functions"""

    def test_calculate_timestamp_today(self):
        """Test calculate_timestamp returns correct format for today"""
        # Create a timestamp for today
        timestamp = timezone.now()
        result = calculate_timestamp(timestamp)
        self.assertIn("today at", result)

    def test_calculate_timestamp_yesterday(self):
        """Test calculate_timestamp returns correct format for yesterday"""
        # Create a timestamp for yesterday
        timestamp = timezone.now() - timedelta(days=1)
        result = calculate_timestamp(timestamp)
        self.assertIn("yesterday at", result)

    def test_calculate_timestamp_other_day(self):
        """Test calculate_timestamp returns correct format for other days"""
        # Create a timestamp for 5 days ago
        timestamp = timezone.now() - timedelta(days=5)
        result = calculate_timestamp(timestamp)
        # Should be in mm/dd/yyyy format
        self.assertIn("/", result)


class BannerTaskTestCase(TestCase):
    """Test banner Celery tasks"""

    def setUp(self):
        from apps.models import Category, State, City, Country, Address

        # Create required objects for Banner
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )
        self.country = Country.objects.create(name="Test Country")
        self.city = City.objects.create(name="Test City", country=self.country)
        self.state = State.objects.create(name="Test State", city=self.city)
        self.address = Address.objects.create(
            state=self.state, longitude=0.0, latitude=0.0
        )
        self.category = Category.objects.create(name="Test Category")

    def test_update_banner_status_task(self):
        """Test banner status update task"""
        from apps.tasks import update_banner_status_task

        # Create an expired banner
        banner = Banner.objects.create(
            title="Test Banner",
            start_time=timezone.now() - timedelta(days=2),
            end_time=timezone.now() - timedelta(days=1),
            category=self.category,
            is_active=True,
        )

        # Run the task
        update_banner_status_task()

        # Refresh from database
        banner.refresh_from_db()

        # Banner should now be inactive
        self.assertFalse(banner.is_active)

    def test_update_banner_status_task_active_banner(self):
        """Test banner status update task doesn't affect active banners"""
        from apps.tasks import update_banner_status_task

        # Create a banner that hasn't expired yet
        banner = Banner.objects.create(
            title="Active Banner",
            start_time=timezone.now() - timedelta(days=1),
            end_time=timezone.now() + timedelta(days=1),
            category=self.category,
            is_active=True,
        )

        # Run the task
        update_banner_status_task()

        # Refresh from database
        banner.refresh_from_db()

        # Banner should still be active
        self.assertTrue(banner.is_active)
