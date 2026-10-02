from django.db import models
from orders.models import Order
# Create your models here.

class Payment(models.Model):

    PROVIDER_CHOICES =  (
        ("CASHFREE", "Cashfree"),
    )
    
    STATUS_CHOICES = [
        ("created", "Created"),
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
        ("refunded", "Refunded")
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment"
    )

    provider = models.CharField(
        max_length=50,
        choices=PROVIDER_CHOICES,
        default="CASHFREE"
    )
    provider_order_id = models.CharField(
        max_length=255,
        blank=True
    )

    payment_session_id = models.TextField(
        blank=True,
        null=True,
    )

    provider_payment_id = models.CharField(
        max_length=155,
        blank=True,
        null=True
    )

    currency = models.CharField(
        max_length=10,
        default="INR"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="created"
    )

    raw_response = models.JSONField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.order.id} - {self.status}"