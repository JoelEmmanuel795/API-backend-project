from django.urls import path
from .views import (
    MenuItemViewSet, CategoryViewSet,
    ManagerUserView, DeliveryCrewUserView,
    SetItemOfTheDayView, CartView,
    OrderListCreateView, OrderDetailView
)

# Custom ViewSet routing without trailing slashes
menuitem_list = MenuItemViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
menuitem_detail = MenuItemViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

category_list = CategoryViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
category_detail = CategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

urlpatterns = [
    # Menu items
    path("menu-items", MenuItemViewSet.as_view({'get': 'list', 'post': 'create'}), name="menuitem-list"),
    path("menu-items/<int:pk>", MenuItemViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="menuitem-detail"),

    # Categories
    path("categories", CategoryViewSet.as_view({'get': 'list', 'post': 'create'}), name="category-list"),
    path("categories/<int:pk>", CategoryViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name="category-detail"),

    # Group management
    path("groups/manager/users", ManagerUserView.as_view(), name="manager-users"),
    path("groups/manager/users/<int:user_id>", ManagerUserView.as_view(), name="manager-user-detail"),
    path("groups/deliverycrew/users", DeliveryCrewUserView.as_view(), name="delivery-crew-users"),
    path("groups/deliverycrew/users/<int:user_id>", DeliveryCrewUserView.as_view(), name="delivery-crew-user-detail"),

    # Item of the Day
    path("menu-items/<int:item_id>/set-item-of-the-day", SetItemOfTheDayView.as_view(), name="set-item-of-the-day"),

    # Cart
    path("cart/menu-items", CartView.as_view(), name="cart-items"),

    # Orders for customers
    path("cart/orders", OrderListCreateView.as_view(), name="cart-orders"),
    path("cart/orders/<int:order_id>", OrderDetailView.as_view(), name="cart-order-detail"),

    # Orders for managers and delivery crew
    path("orders", OrderListCreateView.as_view(), name="orders"),
    path("orders/<int:order_id>", OrderDetailView.as_view(), name="order-detail"),
]
