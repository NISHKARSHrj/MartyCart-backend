from rest_framework import serializers

from .models import Order, OrderItem, OrderHamper, OrderHamperItem

# Serialize data into JSON

class OrderItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = OrderItem

        fields = [
            "id",
            "product",
            "product_name",
            "price",
            "quantity",
        ]

class OrderHamperItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderHamperItem
        fields = [
            "product",
            "product_name",
            "quantity",
            "unit_price",
            "total_price",
        ]


class OrderHamperSerializer(serializers.ModelSerializer):
    items = OrderHamperItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = OrderHamper
        fields = [
            "id",
            "name",
            "subtotal",
            "items",
        ]

class OrderSerializer(serializers.ModelSerializer):

    items = OrderItemSerializer(
        many=True,
        read_only=True
    )
    custom_hampers = OrderHamperSerializer(
        many=True,
        read_only=True
    )
    class Meta:
        model = Order

        fields = [
            "id",
            "status",
            "total_amount",
            "custom_hampers",
            "address",
            "items",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "status",
            "total_amount",
            "items",
            "created_at",
            "updated_at",
        ]

