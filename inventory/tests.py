from django.contrib.auth.models import User
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .models import Item


class UserRegistrationTest(APITestCase):
    """Test suite for user registration."""

    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/register/'

    def test_register_user_success(self):
        data = {
            "username": "testuser",
            "password": "password123",
            "email": "testuser@example.com"
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'User registered successfully.')

    def test_register_user_fail(self):
        # Empty username should return 400
        data = {
            "username": "",
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
        data = {
            "username": "testuser",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_invalid_credentials(self):
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
        self.item = Item.objects.create(name="Test Item", description="Item description")
        self.client.force_authenticate(user=self.user)  # Authenticate the user

        self.item_url = '/api/items/'
        self.item_detail_url = f'/api/items/{self.item.id}/'

    def test_create_item(self):
        data = {
            "name": "New Item",
            "description": "New item description"
        }
        response = self.client.post(self.item_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'New Item')

    def test_create_duplicate_item(self):
        # Attempting to create an item with the same name should fail
        data = {
            "name": "Test Item",
            "description": "Duplicate item"
        }
        response = self.client.post(self.item_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Item already exists.')

    def test_get_all_items(self):
        response = self.client.get(self.item_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreater(len(response.data), 0)

    def test_get_item_detail(self):
        response = self.client.get(self.item_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.item.name)

    def test_get_nonexistent_item(self):
        non_existent_url = '/api/items/9999/'
        response = self.client.get(non_existent_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found.')

    def test_update_item(self):
        data = {
            "name": "Updated Item",
            "description": "Updated description"
        }
        response = self.client.put(self.item_detail_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], "Updated Item")

    def test_update_nonexistent_item(self):
        non_existent_url = '/api/items/9999/'
        data = {
            "name": "Updated Nonexistent Item",
            "description": "Updated description"
        }
        response = self.client.put(non_existent_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found.')

    def test_delete_item(self):
        response = self.client.delete(self.item_detail_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_nonexistent_item(self):
        non_existent_url = '/api/items/9999/'
        response = self.client.delete(non_existent_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'Item not found.')
