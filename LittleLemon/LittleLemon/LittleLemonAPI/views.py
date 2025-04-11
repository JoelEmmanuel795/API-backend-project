from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, filters, generics
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User, Group
from django.db import transaction
from .models import MenuItem, Category, Cart, Order, Order_Item
from .serializers import MenuItemSerializer, CategorySerializer, CartSerializer, OrderSerializer, OrderItemSerializer, UserSerializer
from .permissions import IsManager, IsDeliveryCrew
from datetime import date

class MenuItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['category__title']
    ordering_fields = ['price']

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]  # Only admins (or managers if adjusted) can write
        return [IsAuthenticated()]  # Any logged-in user can view

# class MenuItemListView(generics.ListAPIView):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     permission_classes = [IsAuthenticated]
#     filter_backends = [filters.SearchFilter, filters.OrderingFilter]
#     ordering_fields = ['price']
#     search_fields = ['category__title']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            return [IsAdminUser()]  # or IsManager if needed
        return [IsAuthenticated()]

# class CategoryListView(generics.ListAPIView):
#     queryset = Category.objects.all()
#     serializer_class = CategorySerializer
#     permission_classes = [IsAuthenticated]

class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CartSerializer(data=request.data)
        if serializer.is_valid():
            menu_item = serializer.validated_data['menuitem']
            quantity = serializer.validated_data['quantity']
            unit_price = menu_item.price
            total_price = unit_price * quantity
            Cart.objects.create(
                user=request.user,
                menuitem=menu_item,
                quantity=quantity,
                unit_price=unit_price,
                price=total_price
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.groups.filter(name='Manager').exists():
            orders = Order.objects.all()
        elif user.groups.filter(name='DeliveryCrew').exists():
            orders = Order.objects.filter(delivery_crew=user)
        else:
            orders = Order.objects.filter(user=user)
        
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items:
            return Response({"detail": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        
        total = sum(item.price for item in cart_items)
        order = Order.objects.create(user=request.user, total=total, date=date.today())
        
        for item in cart_items:
            Order_Item.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
        cart_items.delete()
        return Response({"order_id": order.id}, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated, IsDeliveryCrew]
    
    def get(self, request, order_id):
        order = get_object_or_404(Order, id=order_id)
        if order.user != request.user and not request.user.groups.filter(name_in=['Manager', 'Delivery crew']).exists():
            return Response({"detail": "You do not have permission to view this order."}, status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        user = request.user
        
        if user.groups.filter(name='Manager').exists():
            delivery_crew_id = request.data.get('delivery_crew')
            status_update = request.data.get('status')
            
            if delivery_crew_id:
                crew_user = get_object_or_404(User, id=delivery_crew_id)
                if not crew_user.groups.filter(name='DeliveryCrew').exists():
                    return Response({"error": "User is not in delivery crew"}, status=status.HTTP_400_BAD_REQUEST)
                order.delivery_crew = crew_user
            
            if status_update is not None:
                order.status = status_update
            order.save()
            return Response({"detail": "Order updated successfully."}, status=status.HTTP_200_OK)
        
        elif user.groups.filter(name="DeliveryCrew").exists():
            if order.delivery_crew != user:
                return Response({"detail": "You do not have permission to update this order."}, status=status.HTTP_403_FORBIDDEN)
            
            status_update = request.data.get('status')
            if status_update in [0, 1]:
                order.status = status_update
                order.save()
                return Response({"detail": "Delivery status updated."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(status=status.HTTP_403_FORBIDDEN)
    
    def delete(self, request, order_id):
        if not request.user.groups.filter(name='Manager').exists():
            return Response({"detail": "You do not have permission to delete this order."}, status=status.HTTP_403_FORBIDDEN)
        order = get_object_or_404(Order, pk=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class SetItemOfTheDayView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, item_id):
        try:
            MenuItem.objects.update(item_of_the_day=False)  # Reset all to False
            item = MenuItem.objects.get(id=item_id)
            item.item_of_the_day = True
            item.save()
            return Response({"detail": f"'{item.title}' is now the item of the day."}, status=status.HTTP_200_OK)
        except MenuItem.DoesNotExist:
            return Response({"error": "Menu item not found."}, status=status.HTTP_404_NOT_FOUND)

class ManagerUserView(APIView): 
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        users = Group.objects.get(name='Manager').user_set.all()
        return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.get(pk=request.data['user_id'])
        manager_group = Group.objects.get(name='Manager')
        manager_group.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)
    
    def delete(self, request, user_id):
        user = User.objects.get(pk=user_id)
        Group.objects.get(name='Manager').user_set.remove(user)
        return Response(status=status.HTTP_200_OK)

class DeliveryCrewUserView(APIView): 
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        users = Group.objects.get(name='DeliveryCrew').user_set.all()
        return Response(UserSerializer(users, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        user = User.objects.get(pk=request.data['user_id'])
        crew_group = Group.objects.get(name='DeliveryCrew')
        crew_group.user_set.add(user)
        return Response(status=status.HTTP_201_CREATED)

    def delete(self, request, user_id):
        user = User.objects.get(pk=user_id)
        Group.objects.get(name='DeliveryCrew').user_set.remove(user)
        return Response(status=status.HTTP_200_OK)
