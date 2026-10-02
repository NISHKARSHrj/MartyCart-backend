from decimal import Decimal
from math import prod

from django.shortcuts import render

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Category, Product, Wishlist
from .serializers import CategorySerializer, ProductSerializer, WishlistSerializer, CustomHamperProductSerializer, CustomHamperCalculateSerializer
# Create your views here.

class CategoryListView(generics.ListAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class CategoryDetailedView(generics.RetrieveAPIView):

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

class ProductListView(generics.ListAPIView):

    queryset = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    filter_backends = [
        filters.SearchFilter,
    ]
    search_fields = [
        "name",
        "description",
        "sku",
        "category__name"
    ]

class CategoryProductsView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_id = self.kwargs["category_id"]
        return (
            Product.objects
            .filter(
                category_id=category_id,
                is_active=True
            )
            .select_related("category")
            .prefetch_related("images")
        )
class ProductDetailView(generics.RetrieveAPIView):

    queryset = (
        Product.objects
        .filter(is_active=True)
        .select_related("category")
        .prefetch_related("images")
    )

    serializer_class = ProductSerializer
    permission_classes = [AllowAny]

class WishlistListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        wishlist = (
            Wishlist.objects
            .filter(user=request.user)
            .select_related(
                "product",
                "product__category"
            )
            .prefetch_related(
                "product__images"
            )
        )

        serializer = WishlistSerializer(
            wishlist,
            many=True
        )

        return Response(serializer.data)


class WishlistAddView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        product_id = request.data.get("product_id")

        if not product_id:
            return Response(
                {
                    "error": "product_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True
            )

        except Product.DoesNotExist:
            return Response(
                {
                    "error": "Product not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item, created = (
            Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
        )

        if not created:
            return Response(
                {
                    "message": "Product already in wishlist."
                },
                status=status.HTTP_200_OK
            )

        serializer = WishlistSerializer(
            wishlist_item
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class WishlistRemoveView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, product_id):

        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product_id=product_id
            )

        except Wishlist.DoesNotExist:
            return Response(
                {
                    "error": "Product not found in wishlist."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item.delete()

        return Response(
            {
                "message": "Product removed from wishlist."
            },
            status=status.HTTP_200_OK
        )

class CustomHamperView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        products = Product.objects.filter(
            is_active=True,
            is_hamper_item=True
        ).prefetch_related("images")
        serializer = CustomHamperProductSerializer(products, many=True)
        return Response(
            {
                "name": "Make Your Own Hamper",
                "products": serializer.data
            }
        )

class CustomHamperCalculateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomHamperCalculateSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        items = serializer.validated_data["items"]

        product_ids = [
            item["product_id"]
            for item in items
        ]

        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True,
            is_hamper_item=True
        )

        product_by_id = {
            product.id: product
            for product in products
        }

        response_items = []
        subtotal = Decimal("0.00")

        for item in items:
            product_id = item["product_id"]
            quantity = item["quantity"]

            product = product_by_id.get(product_id)

            if not product:
                return Response(
                    {
                        "error": (
                            f"product {product_id} is not available in hampers."
                        )
                    },
                    status=400
                )

            if quantity > product.stock:
                return Response(
                    {
                        "error": (
                            f"Only {product.stock} units of product {product.name} are available."
                        )
                    },
                    status=400
                )

            final_price = (
                product.discount_price
                if product.discount_price is not None
                else product.price

            )

            item_total = final_price * quantity
            subtotal += item_total

            response_items.append({
                "product_id": product.id,
                "name": product.name,
                "quantity": quantity,
                "unit_price": str(final_price),
                "total": str(item_total),
            })

        return Response({
            "name": "Make Your Custom Hamper",
            "items": response_items,
            "subtotal": str(subtotal),
        })