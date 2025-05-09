from rest_framework import serializers
from .models import MenuItem, Category, Cart, Order, Order_Item
from django.contrib.auth.models import User, Group

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'slug', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # ✅ this is key!

    class Meta:
        model = MenuItem
        fields = ['id', 'title', 'price', 'featured', 'category', 'item_of_the_day']

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem', 'quantity']

    def to_internal_value(self, data):
        # Convert string title to MenuItem PK
        if 'menuitem' in data and isinstance(data['menuitem'], str):
            try:
                item = MenuItem.objects.get(title=data['menuitem'])
                data['menuitem'] = item.pk
            except MenuItem.DoesNotExist:
                raise serializers.ValidationError({"menuitem": "Menu item not found by title."})
        return super().to_internal_value(data)

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order_Item
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    orderitem_set = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = '__all__'
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']