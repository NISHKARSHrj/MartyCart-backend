from django.db import models
from django.conf import settings

from products.models import Product

# Create your models here.

class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled")
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )
    address = models.ForeignKey(
        "accounts.Address",
        on_delete=models.CASCADE,
        related_name="orders"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )   

    delivery_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def can_change_status(self, new_status):

        allowed_transitions = {
            "pending": [
                "confirmed",
                "cancelled",
            ],

            "confirmed": [
                "processing",
                "cancelled",
            ],

            "processing": [
                "shipped",
                "cancelled",
            ],

            "shipped": [
                "delivered",
            ],

            "delivered": [],

            "cancelled": [],
        }

        return new_status in allowed_transitions.get(
            self.status,
            []
        )


    def change_status(self, new_status):

        if new_status not in dict(self.STATUS_CHOICES):
            raise ValueError(
                f"Invalid order status: {new_status}"
            )

        if not self.can_change_status(new_status):
            raise ValueError(
                f"Cannot change order status "
                f"from '{self.status}' to '{new_status}'."
            )

        self.status = new_status

        self.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
    def __str__(self):
        return f"Order {self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )
    product_name = models.CharField(
        max_length=200
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

class OrderHamper(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="custom_hampers"
    )

    name = models.CharField(
        max_length=150,
        default="Custom Hamper"
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.name} - Order #{self.order.id}"

class OrderHamperItem(models.Model):
    hamper = models.ForeignKey(
        OrderHamper,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    product_name = models.CharField(
        max_length=255
    )

    quantity = models.PositiveIntegerField()

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.product_name} x {self.quantity}"