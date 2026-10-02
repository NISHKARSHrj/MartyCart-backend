from django.contrib import admin
from .models import Address, Profile, PhoneOTP
# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "phone",
        "phone_verified",
        "date_of_birth",
        "gender"
    )
@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display=(
        "full_name",
        "phone",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "postal_code",
        "is_default"
    )
    list_filter = (
        "state",
        "city",
        "is_default"
    )
    search_fields = (
        "full_name",
        "phone",
        "city",
        "postal_code",
    )

@admin.register(PhoneOTP)
class PhoneOTPAdmin(admin.ModelAdmin):
    list_display = (
        "phone",
        "expires_at",
        "attempts",
        "last_sent_at",
        "verified_at",
        "created_at"
    )
    list_filter = (
        "expires_at",
        "attempts",
        "verified_at",
        "created_at"
    )
    search_fields = (
        "phone",
        "otp_hash"
    )