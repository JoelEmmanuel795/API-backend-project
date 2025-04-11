from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CategoryViewSet, MenuItemViewSet,
    ManagerUserView, DeliveryCrewUserView,
    SetItemOfTheDayView, CartView,
    OrderListCreateView, OrderDetailView,
    # CategoryListView, MenuItemListView
)

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'menu-items', MenuItemViewSet, basename='menuitem')

urlpatterns = [
    path('', include(router.urls)),

    # User Group Management
    path('groups/manager/users/', ManagerUserView.as_view(), name='manager-users'),
    path('groups/manager/users/<int:user_id>/', ManagerUserView.as_view(), name='manager-user-detail'),
    path('groups/deliverycrew/users/', DeliveryCrewUserView.as_view(), name='delivery-crew-users'),
    path('groups/deliverycrew/users/<int:user_id>/', DeliveryCrewUserView.as_view(), name='delivery-crew-user-detail'),

    # MenuItem: Item of the Day
    path('menu-items/<int:item_id>/set-item-of-the-day/', SetItemOfTheDayView.as_view(), name='set-item-of-the-day'),

    # Cart Endpoints
    path('cart/menu-items', CartView.as_view(), name='cart-items'),

    # Order Endpoints
    path('orders', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:order_id>', OrderDetailView.as_view(), name='order-detail'),
]
