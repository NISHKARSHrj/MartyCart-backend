from django.contrib import admin
from .models import Cart, CartItem
# Register your models here.

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "created_at",
        "updated_at"
    )

    search_fields = (
        "user__username",
        "user__email"
    )

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = (
        "cart",
        "product",
        "quantity",
        "created_at",
    )

    search_fields = (
        "products__name",
        "cart__user__username",
        "cart__user__email"
    )