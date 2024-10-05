from rest_framework.test import APIClient, APITestCase,override_settings
from rest_framework import status
from django.contrib.auth.models import User
from .models import Item
from django.core.cache import cache

class UserRegistrationTest(APITestCase):
    """Test suite for user registration."""
    
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/'
    
    def test_register_user_success(self):
        """Test successful user registration."""
        data = {
            "username": "testuser",
            "password": "password123",
            "email": "testuser@example.com"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registered successfully.')
    
    def test_register_user_failure(self):
        """Test registration with invalid data."""
        data = {
            "username": "",  # Empty username
            "password": "password123",
            "email": "testuser@example.com"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserLoginTest(APITestCase):
    """Test suite for user login."""

    def setUp(self):
        self.client = APIClient()
        self.login_url = '/api/login/'
        self.user = User.objects.create_user(username="testuser", password="password123")

    def test_login_success(self):
        """Test successful login."""
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
        """Test login with wrong credentials."""
        data = {
            "username": "testuser",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['error'], 'Invalid credentials')



class ItemViewTest(APITestCase):
    """Test suite for item creation, retrieval, update, and deletion."""

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.client.force_authenticate(user=self.user)
        cache.clear()
        self.item = Item.objects.create(name="Test Item", description="Item description", quantity=10, price=100)
        self.item_url = '/api/items/'
        self.item_detail_url = f'/api/items/{self.item.id}/'

    def test_create_item_success(self):
        """Test successful item creation."""
        data = {
            "name": "New Item",
            "description": "New item description",
            "quantity": 10,
            "price": 100
        }
        response = self.client.post(self.item_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Item')

    def test_create_duplicate_item(self):
        """Test duplicate item creation failure."""
        data = {
            "name": "Test Item",  # This name already exists
            "description": "Duplicate item",
            "quantity": 10,
            "price": 100
        }
        response = self.client.post(self.item_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Item already exists.')

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    })
    def test_retrieve_item_success(self):
        # Create your test items
        self.item = Item.objects.create(name="Test Item", description="Item description", quantity=10, price=100)
        item_detail_url = f'/api/items/{self.item.id}/'

        # Clear the cache before each test
        cache.clear()

        # Now call your API
        response = self.client.get(item_detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.item.name)


    def test_update_item_success(self):
        """Test successful item update."""
        data = {
            "name": "Updated Item",
            "description": "Updated description",
            "quantity": 20,
            "price": 150
        }
        response = self.client.put(self.item_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Item")

    def test_update_item_not_found(self):
        """Test updating an item that does not exist."""
        invalid_item_url = '/api/items/999/'  # Non-existent item ID
        data = {
            "name": "Non-existent Item",
            "description": "Updated description",
            "quantity": 20,
            "price": 150
        }
        response = self.client.put(invalid_item_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found.')

    def test_delete_item_success(self):
        """Test successful item deletion."""
        response = self.client.delete(self.item_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_item_not_found(self):
        """Test deleting an item that does not exist."""
        invalid_item_url = '/api/items/999/'  # Non-existent item ID
        response = self.client.delete(invalid_item_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found.')
