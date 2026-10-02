from django.contrib.auth.models import User
from rest_framework import serializers
from django.db import transaction

from .models import Address, Profile, MartyCoinWallet, MartyCoinTransaction
from .services import process_referral_reward
class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    password_confirm = serializers.CharField(
        write_only=True
    )

    phone = serializers.CharField(
        write_only=True,
        required=True
    )

    date_of_birth = serializers.DateField(
        write_only=True,
        required=True
    )

    gender = serializers.ChoiceField(
        choices=Profile.GENDER_CHOICES,
        write_only=True,
        required=True
    )

    referral_code = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "password_confirm",
            "phone",
            "date_of_birth",
            "gender",
            "referral_code"
        ]

    def validate(self, data):

        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({
                "password": "Passwords do not match."
            })

        email = data["email"].lower().strip()

        if User.objects.filter(
            email__iexact=email
        ).exists():
            raise serializers.ValidationError({
                "email": "A user with that email already exists."
            })

        if User.objects.filter(
            username__iexact=data["username"]
        ).exists():
            raise serializers.ValidationError({
                "username": "This username is already taken."
            })

        referral_code = data.get(
            "referral_code",
            ""
        ).strip().upper()

        if referral_code:
            try:
                referrer_profile = Profile.objects.get(
                    referral_code=referral_code
                )
            except Profile.DoesNotExist:
                raise serializers.ValidationError({
                    "referral_code": (
                        "The provided referral code is invalid."
                    )
                })

            data["referrer_profile"] = referrer_profile

        data["email"] = email

        return data

    def validate_phone(self, value):

        value = value.strip()

        if Profile.objects.filter(
            phone=value
        ).exists():
            raise serializers.ValidationError({
                "phone": (
                    "A user with that phone number "
                    "already exists."
                )
            })

        return value
    @transaction.atomic
    def create(self, validated_data):

        validated_data.pop("password_confirm")

        password = validated_data.pop("password")

        phone = validated_data.pop("phone")

        date_of_birth = validated_data.pop(
            "date_of_birth"
        )

        gender = validated_data.pop("gender")

        referrer_profile = validated_data.pop(
            "referrer_profile",
            None
        )

        validated_data.pop(
            "referral_code",
            None
        )

        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=password,
            first_name=validated_data.get(
                "first_name",
                ""
            ),
            last_name=validated_data.get(
                "last_name",
                ""
            )
        )

        Profile.objects.create(
            user=user,
            phone=phone,
            date_of_birth=date_of_birth,
            gender=gender,
            referred_by=(
                referrer_profile.user
                if referrer_profile
                else None
            )
        )
        MartyCoinWallet.objects.create(user=user)

        if referrer_profile:
            process_referral_reward(new_user=user, referrer_user=referrer_profile.user)
        return user

class ProfileSerializer(serializers.ModelSerializer):

    referral_code = serializers.CharField(read_only=True)

    referred_users_count = serializers.SerializerMethodField()
    class Meta:
        model = Profile
        fields = [
            "phone",
            "date_of_birth",
            "gender",
            "referral_code",
            "referred_users_count",
        ]

    def get_referred_users_count(self, obj):
        return obj.user.referred_users.count()

class UserSerializer(serializers.ModelSerializer):

    profile = ProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile",
        ]
        read_only_fields = [
            "id",
            "username",
            "email",
        ]

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = [
            "id",
            "full_name",
            "phone",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "postal_code",
            "country",
            "is_default",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "created_at"
        ]

class ReferredUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "date_joined",
        ]

class MartyCoinTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MartyCoinTransaction
        fields = [
            "id",
            "transaction_type",
            "amount",
            "description",
            "reference",
            "reference_type",
            "created_at",
        ]

class MartyCoinWalletSerializer(serializers.ModelSerializer):
    transactions = MartyCoinTransactionSerializer(many=True, read_only=True)
    
    class Meta:
        model = MartyCoinWallet
        fields = [
            "balance",
            "transactions",
        ]

class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=15)
    otp = serializers.CharField(
        min_length=6,
        max_length=6
    )