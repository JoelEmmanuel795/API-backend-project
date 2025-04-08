from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menuitems', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),
    path('groups/manager/users/', ManagerUserView.as_view(), name='manager-users'),
    path('groups/manager/users/<int:user_id>/', ManagerUserView.as_view(), name='manager-user-detail'),
    path('groups/deliverycrew/users/', DeliveryCrewUserView.as_view(), name='delivery-crew-users'),
    path('groups/deliverycrew/users/<int:user_id>/', DeliveryCrewUserView.as_view(), name='delivery-crew-user-detail'),
    path('menuitems/<int:item_id>/set-item-of-the-day/', SetItemOfTheDayView.as_view(), name='set-item-of-the-day'),
]