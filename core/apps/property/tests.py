from django.test import TestCase
from django.contrib.auth import get_user_model
from django.test import Client
import json

User = get_user_model()


class PropertyViewTestCase(TestCase):
    """Test property API views"""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="owner@example.com", username="owner", password="testpass123"
        )
        from apps.models import Category, State, City, Country, Address

        self.country = Country.objects.create(name="Test Country")
        self.city = City.objects.create(name="Test City", country=self.country)
        self.state = State.objects.create(name="Test State", city=self.city)
        self.address = Address.objects.create(
            state=self.state, longitude=0.0, latitude=0.0
        )
        self.category = Category.objects.create(name="Test Category")

    def test_property_list_view(self):
        """Test property list endpoint"""
        response = self.client.get("/api/property/")
        self.assertIn(response.status_code, [200, 401])

    def test_property_create_view_unauthenticated(self):
        """Test property creation without authentication"""
        data = {
            "name": "Test Property",
            "description": "A test property",
            "size": 100,
            "price": 500000,
            "category": self.category.id,
            "address": self.address.id,
        }
        response = self.client.post(
            "/api/property/", data=json.dumps(data), content_type="application/json"
        )
        self.assertIn(response.status_code, [401, 403, 400])


class CategoryViewTestCase(TestCase):
    """Test category API views"""

    def setUp(self):
        self.client = Client()

    def test_category_list_view(self):
        """Test category list endpoint"""
        response = self.client.get("/api/categorie/")
        self.assertIn(response.status_code, [200, 401])


class AddressViewTestCase(TestCase):
    """Test address API views"""

    def setUp(self):
        self.client = Client()

    def test_address_country_view(self):
        """Test address country endpoint"""
        response = self.client.get("/api/address/country/")
        self.assertIn(response.status_code, [200, 401])


class HealthCheckTestCase(TestCase):
    """Test health check endpoint"""

    def setUp(self):
        self.client = Client()

    def test_health_check(self):
        """Test health endpoint"""
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
