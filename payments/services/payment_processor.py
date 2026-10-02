from django.db import transaction

from payments.models import Payment
from orders.models import Order
from cart.models import CartItem


@transaction.atomic
def process_successful_payment(
    payment,
    provider_payment_id=None,
):
    order = (
        Order.objects
        .select_for_update()
        .get(id=payment.order_id)
    )

    payment = (
        Payment.objects
        .select_for_update()
        .get(id=payment.id)
    )

    # Idempotency:
    # Agar webhook same payment ke liye dobara aaye,
    # dobara stock reduce nahi hoga.
    if payment.status == "success":
        return order

    # Order already completed
    if order.status != "pending":
        payment.status = "success"
        if provider_payment_id:
            payment.provider_payment_id = provider_payment_id
        payment.save(
            update_fields=[
                "status",
                "provider_payment_id",
                "updated_at",
            ]
        )
        return order

    # Stock verify + reduce
    for item in order.items.select_for_update().all():

        if item.product.stock < item.quantity:
            raise ValueError(
                f"Insufficient stock for {item.product_name}"
            )

        item.product.stock -= item.quantity
        item.product.save(
            update_fields=["stock"]
        )

    # Payment successful
    payment.status = "success"

    if provider_payment_id:
        payment.provider_payment_id = provider_payment_id

    payment.save()

    # Confirm order
    order.status = "confirmed"
    order.save(update_fields=["status", "updated_at"])

    # Clear user's cart
    CartItem.objects.filter(
        cart__user=order.user
    ).delete()

    return order