from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer

from .models import Cart, CartItem, CustomHamper, CustomHamperItem

# serializer DATA into JSON

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.filter(is_active=True),
        source="product",
        write_only=True,
    )

    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_id",
            "quantity",
            "subtotal",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "subtotal",
            "created_at",
            "updated_at",
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1")
        return value

    def validate(self, data):
        product = data.get("product")
        quantity = data.get("quantity")

        if product and quantity > product.stock:
            raise serializers.ValidationError({
                "quantity": f"only {product.stock} items available."
            })
        return data

    def get_subtotal(self, obj):
        price = (
            obj.product.discount_price
            if obj.product.discount_price is not None
            else obj.product.price
        )
        return price * obj.quantity

class CustomHamperItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source="product.name",
        read_only=True
    )

    class Meta:
        model = CustomHamperItem
        fields = [
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
        ]

class CustomHamperSerializer(serializers.ModelSerializer):
    items = CustomHamperItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = CustomHamper
        fields = [
            "id",
            "name",
            "subtotal",
            "items",
            "created_at",
            "updated_at",
        ]
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    custom_hampers = CustomHamperSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = Cart
        fields = [
            "id",
            "items",
            "custom_hampers",
            "total",
            "created_at",
            "updated_at",
        ]

    def get_total(self, obj):
        total = 0
        for item in obj.items.all():
            price = (
                item.product.discount_price
                if item.product.discount_price is not None
                else item.product.price
            )
            total += price * item.quantity
        return total




