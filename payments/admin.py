from django.contrib import admin
from .models import Payment
# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "provider",
        "amount",
        "status",
        "created_at"
    )
    list_filter = (
        "provider",
        "status",
        "created_at"
    )
    search_fields = (
        "payment_order_id",
        "payment_id",
        "order__user__username",
        "order__user__email",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )