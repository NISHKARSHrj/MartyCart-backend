from decimal import Decimal

from django.conf import settings
from django.db import transaction

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from accounts.models import Address
from cart.models import Cart

from .models import (
    Order,
    OrderItem,
    OrderHamper,
    OrderHamperItem,
)
from .serializers import OrderSerializer


class OrderListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):

        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                "items",
                "custom_hampers__items",
            )
            .order_by("-created_at")
        )

    @transaction.atomic
    def create(self, request, *args, **kwargs):

        address_id = request.data.get("address_id")

        if not address_id:
            return Response(
                {
                    "detail": "address_id is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:

            address = Address.objects.get(
                id=address_id,
                user=request.user
            )

        except Address.DoesNotExist:

            return Response(
                {
                    "detail": "Address not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        try:

            cart = Cart.objects.prefetch_related(
                "items__product",
                "custom_hampers__items__product",
            ).get(
                user=request.user
            )

        except Cart.DoesNotExist:

            return Response(
                {
                    "detail": "Cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = cart.items.all()
        custom_hampers = cart.custom_hampers.all()

        if not cart_items.exists() and not custom_hampers.exists():

            return Response(
                {
                    "detail": "Cart is empty."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        normal_items_total = Decimal("0.00")
        custom_hampers_total = Decimal("0.00")

        
        for cart_item in cart_items:

            product = cart_item.product

            if not product.is_active:

                return Response(
                    {
                        "detail": (
                            f"{product.name} is no longer available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if cart_item.quantity > product.stock:

                return Response(
                    {
                        "detail": (
                            f"Only {product.stock} "
                            f"of {product.name} "
                            "are available."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            price = (
                product.discount_price
                if product.discount_price is not None
                else product.price
            )

            item_total = price * cart_item.quantity

            normal_items_total += item_total

        

        for cart_hamper in custom_hampers:

            hamper_total = Decimal("0.00")

            for hamper_item in cart_hamper.items.all():

                product = hamper_item.product

                if not product.is_active:

                    return Response(
                        {
                            "detail": (
                                f"{product.name} is no longer "
                                "available."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                if hamper_item.quantity > product.stock:

                    return Response(
                        {
                            "detail": (
                                f"Only {product.stock} "
                                f"of {product.name} "
                                "are available."
                            )
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                price = (
                    product.discount_price
                    if product.discount_price is not None
                    else product.price
                )

                item_total = price * hamper_item.quantity

                hamper_total += item_total

            custom_hampers_total += hamper_total

        
        subtotal = (
            normal_items_total +
            custom_hampers_total
        )

        delivery_fee = Decimal(
            str(settings.DELIVERY_FEE)
        )

        total_amount = (
            subtotal +
            delivery_fee
        )


        order = Order.objects.create(
            user=request.user,
            address=address,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
            status="pending",
        )

        for cart_item in cart_items:

            product = cart_item.product

            price = (
                product.discount_price
                if product.discount_price is not None
                else product.price
            )

            item_total = price * cart_item.quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                price=price,
                quantity=cart_item.quantity,
                unit_price=price,
                total_price=item_total,
            )


        for cart_hamper in custom_hampers:

            hamper_total = Decimal("0.00")

            for hamper_item in cart_hamper.items.all():

                product = hamper_item.product

                price = (
                    product.discount_price
                    if product.discount_price is not None
                    else product.price
                )

                item_total = (
                    price * hamper_item.quantity
                )

                hamper_total += item_total

            order_hamper = OrderHamper.objects.create(
                order=order,
                name=cart_hamper.name,
                subtotal=hamper_total,
            )

            for hamper_item in cart_hamper.items.all():

                product = hamper_item.product

                price = (
                    product.discount_price
                    if product.discount_price is not None
                    else product.price
                )

                item_total = (
                    price * hamper_item.quantity
                )

                OrderHamperItem.objects.create(
                    hamper=order_hamper,
                    product=product,
                    product_name=product.name,
                    quantity=hamper_item.quantity,
                    unit_price=price,
                    total_price=item_total,
                )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )


class OrderDetailView(generics.RetrieveAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):

        return (
            Order.objects
            .filter(user=self.request.user)
            .prefetch_related(
                "items",
                "custom_hampers__items",
            )
        )

class OrderStatusUpdateView(generics.UpdateAPIView):

    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = OrderSerializer

    queryset = Order.objects.all()

    http_method_names = ["patch"]

    def patch(self, request, *args, **kwargs):

        order = self.get_object()

        new_status = request.data.get("status")

        if not new_status:
            return Response(
                {
                    "detail": "Status is required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )

class OrderCancelView(generics.GenericAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        )

    @transaction.atomic
    def post(self, request, *args, **kwargs):

        order = self.get_object()

        if order.status not in [
            "pending",
            "confirmed",
        ]:
            return Response(
                {
                    "detail": (
                        f"Order cannot be cancelled "
                        f"while it is '{order.status}'."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.change_status("cancelled")

        return Response(
            OrderSerializer(order).data,
            status=status.HTTP_200_OK
        )