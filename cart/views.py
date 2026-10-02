from decimal import Decimal

from django.db import transaction

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from .models import Cart, CartItem, CustomHamperItem, CustomHamper
from .serializers import CartSerializer, CartItemSerializer, CustomHamperSerializer


class CartView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        return Response(
            CartSerializer(cart).data
        )


class CartItemCreateView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        serializer = CartItemSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        product = serializer.validated_data["product"]
        quantity = serializer.validated_data["quantity"]

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": quantity
            }
        )

        if not created:

            new_quantity = item.quantity + quantity

            if new_quantity > product.stock:
                return Response(
                    {
                        "detail": (
                            f"Only {product.stock} "
                            "items are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity = new_quantity
            item.save()

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED
        )


class CartItemUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):

        try:
            item = CartItem.objects.get(
                pk=pk,
                cart__user=request.user
            )

        except CartItem.DoesNotExist:

            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CartItemSerializer(
            item,
            data=request.data,
            partial=True
        )

        serializer.is_valid(
            raise_exception=True
        )

        serializer.save()

        return Response(
            CartItemSerializer(item).data
        )


class CartItemDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):

        try:
            item = CartItem.objects.get(
                pk=pk,
                cart__user=request.user
            )

        except CartItem.DoesNotExist:

            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )

class AddCustomHamperToCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):

        items = request.data.get("items")

        if not items:
            return Response(
                {
                    "error": "At least one product is required."
                },
                status=400
            )

        cart, _ = Cart.objects.get_or_create(
            user=request.user
        )

        product_ids = [
            item.get("product_id")
            for item in items
        ]

        products = Product.objects.filter(
            id__in=product_ids,
            is_active=True,
            is_hamper_item=True
        )

        products_by_id = {
            product.id: product
            for product in products
        }

        # Create hamper
        hamper = CustomHamper.objects.create(
            cart=cart,
            name="Custom Hamper"
        )

        subtotal = Decimal("0.00")

        for item in items:

            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id or not quantity:
                return Response(
                    {
                        "error": "product_id and quantity are required."
                    },
                    status=400
                )

            if quantity < 1:
                return Response(
                    {
                        "error": "Quantity must be at least 1."
                    },
                    status=400
                )

            product = products_by_id.get(product_id)

            if not product:
                return Response(
                    {
                        "error": (
                            f"Product {product_id} is not "
                            "available for custom hampers."
                        )
                    },
                    status=400
                )

            if quantity > product.stock:
                return Response(
                    {
                        "error": (
                            f"Only {product.stock} units of "
                            f"{product.name} are available."
                        )
                    },
                    status=400
                )

            unit_price = (
                product.discount_price
                if product.discount_price is not None
                else product.price
            )

            total_price = unit_price * quantity

            subtotal += total_price

            CustomHamperItem.objects.create(
                hamper=hamper,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )

        hamper.subtotal = subtotal
        hamper.save(
            update_fields=["subtotal", "updated_at"]
        )

        return Response(
            {
                "message": "Custom hamper added to cart.",
                "hamper": CustomHamperSerializer(
                    hamper
                ).data
            },
            status=201
        )