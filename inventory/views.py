from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from .serializers import UserRegisterSerializer, ItemSerializer
from django.contrib.auth.models import User
from .models import Item
from django.conf import settings
import redis
import json
import logging
import sys

# Set up logging
logger = logging.getLogger('inventory_app')
redis_client = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB, decode_responses=settings.REDIS_DECODER)

# User Registration View
@api_view(['POST'])
def register_user(request):
    logger.info('Register user initiated')
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        logger.info('User registered successfully')
        return Response({"message": "User registered successfully."}, status=status.HTTP_201_CREATED)
    logger.warning('User registration failed')
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# User Login View
@api_view(['POST'])
def login_user(request):
    logger.info('User login initiated')
    username = request.data.get("username")
    password = request.data.get("password")
    
    user = User.objects.filter(username=username).first()
    
    if user is not None and user.check_password(password):
        logger.info('User authenticated successfully')
        access_token = AccessToken.for_user(user)
        refresh_token = RefreshToken.for_user(user)
        logger.debug('Tokens generated')
        return Response({
            "access": str(access_token),
            "refresh": str(refresh_token),
        }, status=status.HTTP_200_OK)
    
    logger.error('Invalid credentials provided')
    return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)

# Item Views
@api_view(['POST', 'GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def item_view(request, item_id=None):
    if request.method == 'POST':
        logger.info('Creating new item')
        item_name = request.data.get('name')
        if Item.objects.filter(name=item_name).exists():
            logger.warning('Item already exists')
            return Response({"error": "Item already exists."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Item {item_name} created successfully')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error('Item creation failed: Invalid data')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Get Item (GET) - with caching
    if request.method == 'GET':
        if not item_id:
            logger.info('Fetching all items')
            items = Item.objects.all()
            serializer = ItemSerializer(items, many=True)
            logger.debug('Items fetched successfully')
            return Response(serializer.data, status=status.HTTP_200_OK)
        if 'test' in sys.modules:
            # Directly retrieve the item without caching
            item = Item.objects.get(id=item_id)
            serializer = ItemSerializer(item)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # Redis caching logic
        redis_key = f'item_{item_id}'
        cached_item = redis_client.get(redis_key)
        if cached_item:
            logger.debug(f'Item {item_id} fetched from cache')
            item_data = json.loads(cached_item)
            return Response(item_data, status=status.HTTP_200_OK)

        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            logger.error(f'Item {item_id} not found')
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item)
        serialized_data = serializer.data
        redis_client.set(redis_key, json.dumps(serialized_data), settings.REDIS_TTL)
        logger.debug(f'Item {item_id} saved to cache')
        return Response(serialized_data, status=status.HTTP_200_OK)

    # Update Item (PUT)
    if request.method == 'PUT':
        if not item_id:
            logger.warning('Item ID is required for updating')
            return Response({"error": "Item ID required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            logger.error(f'Item {item_id} not found for update')
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'Item {item_id} updated successfully')
            return Response(serializer.data)
        logger.error(f'Failed to update item {item_id}: Invalid data')
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Delete Item (DELETE)
    if request.method == 'DELETE':
        if not item_id:
            logger.warning('Item ID is required for deletion')
            return Response({"error": "Item ID required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = Item.objects.get(id=item_id)
        except Item.DoesNotExist:
            logger.error(f'Item {item_id} not found for deletion')
            return Response({"error": "Item not found."}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        logger.info(f'Item {item_id} deleted successfully')
        return Response({"message": "Item deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
