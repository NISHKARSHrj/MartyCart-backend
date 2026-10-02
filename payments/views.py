import base64
import hashlib
import hmac
import json
import os

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from orders.models import Order
from .models import Payment
from .services.cashfree import create_cashfree_order

from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from .models import Payment
from .services.payment_processor import process_successful_payment

class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        order_id = request.data.get("order_id")

        if not order_id:
            return Response(
                {"error": "order_id is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user,
            )
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status != "pending":
            return Response(
                {
                    "error": "Payment cannot be created for this order"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment, created = Payment.objects.get_or_create(
            order=order,
            defaults={
                "provider_order_id": f"pending_{order.id}",
                "amount": order.total_amount,
                "currency": "INR",
                "provider": "cashfree",
                "status": "created",
            },
        )

        # Existing Cashfree payment can be handled here later.
        # For now, create a fresh Cashfree order.

        cashfree_response = create_cashfree_order(
            order_id=order.id,
            amount=order.total_amount,
            customer_id=request.user.id,
            customer_name=(
                request.user.get_full_name()
                or request.user.username
            ),
            customer_email=request.user.email,
            customer_phone="9999999999",
        )

        payment.provider_order_id = cashfree_response["order_id"]
        payment.payment_session_id = (
            cashfree_response["payment_session_id"]
        )
        payment.amount = order.total_amount
        payment.currency = "INR"
        payment.status = "pending"
        payment.raw_response = cashfree_response
        payment.save()

        return Response(
            {
                "order_id": order.id,
                "payment_session_id": (
                    payment.payment_session_id
                ),
                "amount": str(payment.amount),
                "currency": payment.currency,
            },
            status=status.HTTP_201_CREATED,
        )

class CashfreeWebhookView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):

        signature = request.headers.get(
            "x-webhook-signature"
        )

        timestamp = request.headers.get(
            "x-webhook-timestamp"
        )

        if not signature or not timestamp:
            return HttpResponse(
                "Missing webhook signature",
                status=400,
            )

        client_secret = os.getenv(
            "CASHFREE_CLIENT_SECRET"
        )

        if not client_secret:
            return HttpResponse(
                "Cashfree secret not configured",
                status=500,
            )

        raw_body = request.body.decode("utf-8")

        signed_payload = (
            timestamp + raw_body
        )

        expected_signature = base64.b64encode(
            hmac.new(
                client_secret.encode("utf-8"),
                signed_payload.encode("utf-8"),
                hashlib.sha256,
            ).digest()
        ).decode("utf-8")

        if not hmac.compare_digest(
            signature,
            expected_signature,
        ):
            return HttpResponse(
                "Invalid signature",
                status=401,
            )

        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            return HttpResponse(
                "Invalid JSON",
                status=400,
            )

        event_type = data.get("type")

        print(
            f"Cashfree webhook received: {event_type}"
        )

        # Payment success event
        if event_type == "PAYMENT_SUCCESS_WEBHOOK":

            payment_data = data.get(
                "data",
                {}
            )

            order_data = payment_data.get(
                "order",
                {}
            )

            payment_details = payment_data.get(
                "payment",
                {}
            )

            cashfree_order_id = order_data.get(
                "order_id"
            )

            provider_payment_id = payment_details.get(
                "cf_payment_id"
            )

            if not cashfree_order_id:
                return HttpResponse(
                    "Missing order_id",
                    status=400,
                )

            try:
                payment = Payment.objects.get(
                    provider_order_id=cashfree_order_id
                )
            except Payment.DoesNotExist:
                return HttpResponse(
                    "Payment not found",
                    status=404,
                )

            try:
                process_successful_payment(
                    payment=payment,
                    provider_payment_id=(
                        provider_payment_id
                    ),
                )
            except ValueError as error:
                return HttpResponse(
                    str(error),
                    status=400,
                )

        return HttpResponse(
            "Webhook processed",
            status=200,
        )