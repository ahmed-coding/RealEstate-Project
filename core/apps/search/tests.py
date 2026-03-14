from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.search.models import SearchQueryLog, PropertyEmbedding

User = get_user_model()


class SearchQueryLogTestCase(TestCase):
    """Test SearchQueryLog model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email="test@example.com", username="testuser", password="testpass123"
        )

    def test_search_query_log_creation(self):
        """Test creating a search query log"""
        log = SearchQueryLog.objects.create(
            user=self.user,
            query="luxury apartment",
            search_type="hybrid",
            results_count=10,
        )
        self.assertEqual(log.query, "luxury apartment")
        self.assertEqual(log.search_type, "hybrid")
        self.assertEqual(log.results_count, 10)

    def test_search_query_log_without_user(self):
        """Test creating a search query log without user"""
        log = SearchQueryLog.objects.create(
            query="villa for rent",
            search_type="semantic",
            results_count=5,
        )
        self.assertIsNone(log.user)
        self.assertEqual(log.query, "villa for rent")

    def test_search_query_log_str(self):
        """Test string representation"""
        log = SearchQueryLog.objects.create(
            query="beach house",
            search_type="keyword",
            results_count=3,
        )
        self.assertEqual(str(log), "beach house - keyword")


class PropertyEmbeddingTestCase(TestCase):
    """Test PropertyEmbedding model"""

    def setUp(self):
        from apps.models import Category, State, City, Country, Address, Property

        # Create required objects for Property
        self.user = User.objects.create_user(
            email="owner@example.com", username="owner", password="testpass123"
        )
        self.country = Country.objects.create(name="Test Country")
        self.city = City.objects.create(name="Test City", country=self.country)
        self.state = State.objects.create(name="Test State", city=self.city)
        self.address = Address.objects.create(
            state=self.state, longitude=0.0, latitude=0.0
        )
        self.category = Category.objects.create(name="Test Category")

        # Create a property
        self.property = Property.objects.create(
            user=self.user,
            category=self.category,
            address=self.address,
            name="Test Property",
            description="A test property",
            size=100,
            price=500000,
        )

    def test_property_embedding_creation(self):
        """Test creating a property embedding"""
        embedding = PropertyEmbedding.objects.create(
            property=self.property,
            embedding=[0.1] * 1536,
            embedded_text="Test Property - A test property",
            embedding_model="text-embedding-3-small",
        )
        self.assertEqual(embedding.property, self.property)
        self.assertEqual(len(embedding.embedding), 1536)
        self.assertEqual(embedding.embedding_model, "text-embedding-3-small")

    def test_property_embedding_str(self):
        """Test string representation"""
        embedding = PropertyEmbedding.objects.create(
            property=self.property,
            embedding=[0.1] * 1536,
            embedded_text="Test Property",
        )
        self.assertEqual(str(embedding), "Embedding for Test Property")

    def test_property_embedding_update(self):
        """Test updating a property embedding"""
        embedding = PropertyEmbedding.objects.create(
            property=self.property,
            embedding=[0.1] * 1536,
            embedded_text="Original text",
        )

        # Update embedding
        new_embedding = [0.2] * 1536
        embedding.embedding = new_embedding
        embedding.embedded_text = "Updated text"
        embedding.save()

        # Refresh from database
        embedding.refresh_from_db()

        self.assertEqual(embedding.embedded_text, "Updated text")
