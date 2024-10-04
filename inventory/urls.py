from django.urls import path
from . import views as v
from rest_framework_simplejwt.views import TokenObtainPairView

urlpatterns = [
    path('register/', v.register_user, name='register'),
    path('login/', v.login_user, name='login'),
    path('items/', v.item_view, name='create-item'),  # POST: Create item
    path('items/<int:item_id>/', v.item_view, name='item-detail'),

]
