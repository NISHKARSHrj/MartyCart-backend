from rest_framework import serializers
from .models import Category, Product, ProductImage, Wishlist

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            "id",
            "name",
            "slug",
            "description"
        ]

class ProductImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductImage
        fields = [
            "id",
            "image",
            "alt_text",
            "is_primary",
        ]

class ProductSerializer(serializers.ModelSerializer):

    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)

    class Meta: 
        model = Product

        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "discount_price",
            "sku",
            "stock",
            "is_active",
            "category",
            "images",
            "created_at",
            "updated_at"
        ]

class WishlistSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist

        fields = [
            "id",
            "product",
            "created_at"
        ]

        read_only_fields = [
            "id",
            "product",
            "created_at"
        ]

class CustomHamperProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(
        many=True,
        read_only=True
    )

    final_price = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "discount_price",
            "sku",
            "stock",
            "is_active",
            "is_hamper_item",
            "images",
            "final_price"
        ]

    def get_final_price(self, obj):
        if obj.discount_price is not None:
            return obj.discount_price

        return obj.price

class CustomHamperCalculateItemSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1)

class CustomHamperCalculateSerializer(serializers.Serializer):
    items = CustomHamperCalculateItemSerializer(many=True)

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "At least one product is required"
            )
        return value
    