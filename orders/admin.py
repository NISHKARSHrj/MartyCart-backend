from django.contrib import admin
from .models import Order, OrderItem, OrderHamper, OrderHamperItem
# Register your models here.

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "total_amount",
        "created_at",
    )
    list_filter = (
        "status",
        "created_at"
    )

    search_fields = (
        "user__username",
        "user__email"
    )

    readonly_fields = (
        "created_at",
        "updated_at"
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "product_name",
        "price",
        "quantity",
    )
    search_fields = (
        "product_name",
        "order__user__username",
        "order__user__email",
    )

@admin.register(OrderHamper)
class OrderHamperAdmin(admin.ModelAdmin):
    list_display = (
        "order",
        "name",
        "subtotal",
    )
    search_fields = (
        "name",
        "order__user__username",
        "order__user__email",
    )


@admin.register(OrderHamperItem)
class OrderHamperItemAdmin(admin.ModelAdmin):
    list_display = (
        "hamper",
        "product",
        "product_name",
        "unit_price",
        "total_price",
        "quantity",
    )
    search_fields = (
        "product_name",
        "hamper__name",
        "hamper__order__user__username",
        "hamper__order__user__email",
    )