from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

import secrets
import string
# Create your models here.

class Address(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    address_line1 = models.CharField(max_length=255)

    address_line2 = models.CharField(
        max_length=255,
        blank=True
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)

    country = models.CharField(
        max_length=100,
        default="India"
    )

    is_default = models.BooleanField(
        default=False
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.city}"

class Profile(models.Model):

    GENDER_CHOICES = (
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other")
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )
    phone_verified = models.BooleanField(
        default=False
    )
    date_of_birth = models.DateField(
        blank=True,
        null=True
    )

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    referral_code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    referred_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="referred_users"
    )

    def generate_referral_code(self):
        characters = string.ascii_uppercase + string.digits

        return "MARTY" + "".join(secrets.choice(characters) for _ in range(8))

    def save(self, *args, **kwargs):

        if not self.referral_code:
            code =  self.generate_referral_code()

            while Profile.objects.filter(
                referral_code=code
            ).exists():
                code = self.generate_referral_code()

            self.referral_code = code

        super().save(*args, **kwargs)


    def __str__(self):
        return self.user.email or self.user.username
class PhoneOTP(models.Model):

    phone = models.CharField(
        max_length=15,
        db_index=True,
    )

    otp_hash = models.CharField(
        max_length=128
    )

    expires_at = models.DateTimeField()

    attempts = models.PositiveIntegerField(
        default=0
    )

    last_sent_at = models.DateTimeField(
        auto_now_add=True
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.phone
class MartyCoinWallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="martycoin_wallet"
    )

    balance = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.balance} MartyCoins"


class MartyCoinTransaction(models.Model):

    TRANSACTION_TYPES = (
        ("earned", "Earned"),
        ("spent", "Spent"),
        ("refunded", "Refunded"),
        ("adjustment", "Adjustment"),
    )

    wallet = models.ForeignKey(
        MartyCoinWallet,
        on_delete=models.CASCADE,
        related_name="transactions"
    )

    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES
    )

    amount = models.PositiveIntegerField()

    description = models.CharField(
        max_length=255
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    reference_type = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.wallet.user.username} - "
            f"{self.transaction_type} - "
            f"{self.amount}"
        )