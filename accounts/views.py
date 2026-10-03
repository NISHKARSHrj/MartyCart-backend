from django.shortcuts import render
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.models import User

from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Address, MartyCoinWallet, PendingRegistration, Profile, PhoneOTP
from .serializers import RegisterSerializer, AddressSerializer, UserSerializer, ReferredUserSerializer, MartyCoinWalletSerializer
from .services.services import verify_phone_otp, hash_otp, process_referral_reward

# Create your views here.


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serialzer = RegisterSerializer(data=request.data)

        serialzer.is_valid(raise_exception=True)

        pending = serialzer.save()

        return Response(
            {
                "message": "Registration successful.",
                "phone": pending.phone,
                "expires_at": pending.expires_at
            },
            status=status.HTTP_201_CREATED
        )
    

class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class AddressListCreateView(generics.ListCreateAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):

        return Address.objects.filter(
            user=self.request.user
        )

    def perform_create(self, serializer):

        serializer.save(
            user=self.request.user
        )

class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):

    permission_classes = [IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):

        return Address.objects.filter(
            user=self.request.user
        )

class ReferralListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        referred_users = User.objects.filter(profile__referred_by=request.user).order_by("-date_joined")

        serializer = ReferredUserSerializer(referred_users, many=True)

        return Response(
            {
                "referral_code": request.user.profile.referral_code,
                "total_referred": referred_users.count(),
                "referrals": serializer.data
            }
        )

class WalletView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        wallet, _ = MartyCoinWallet.objects.get_or_create(
            user=request.user
        )

        serializer = MartyCoinWalletSerializer(wallet)

        return Response(serializer.data)

class VerifyRegistrationOTPView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):

        phone = request.data.get("phone")
        otp = request.data.get("otp")

        if not phone:
            return Response(
                {"error": "phone is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp:
            return Response(
                {"error": "otp is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending = (
            PendingRegistration.objects
            .select_for_update()
            .filter(phone=phone)
            .order_by("-created_at")
            .first()
        )

        if not pending:
            return Response(
                {
                    "error":
                    "No pending registration found."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if timezone.now() > pending.expires_at:

            pending.delete()

            return Response(
                {
                    "error":
                    "Registration expired. Please register again."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_record = (
            PhoneOTP.objects
            .select_for_update()
            .filter(
                phone=phone,
                verified_at__isnull=True,
            )
            .order_by("-created_at")
            .first()
        )

        if not otp_record:
            return Response(
                {
                    "error":
                    "OTP not found."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if timezone.now() > otp_record.expires_at:
            return Response(
                {
                    "error":
                    "OTP has expired."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp_record.attempts >= 5:
            return Response(
                {
                    "error":
                    "Too many attempts."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Count attempt
        otp_record.attempts += 1
        otp_record.save(
            update_fields=["attempts"]
        )

        if otp_record.otp_hash != hash_otp(otp):
            return Response(
                {
                    "error":
                    "Invalid OTP."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_record.verified_at = timezone.now()

        otp_record.save(
            update_fields=["verified_at"]
        )

        if User.objects.filter(
            username=pending.username
        ).exists():

            return Response(
                {
                    "error":
                    "Username is already taken."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(
            email__iexact=pending.email
        ).exists():

            return Response(
                {
                    "error":
                    "Email is already registered."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Profile.objects.filter(
            phone=pending.phone
        ).exists():

            return Response(
                {
                    "error":
                    "Phone number is already registered."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create(
            username=pending.username,
            email=pending.email,
            password=pending.password_hash,
            first_name=pending.first_name,
            last_name=pending.last_name,
        )

        referrer_profile = None

        if pending.referral_code:

            referrer_profile = (
                Profile.objects
                .filter(
                    referral_code=pending.referral_code
                )
                .first()
            )

        profile = Profile.objects.create(
            user=user,
            phone=pending.phone,
            phone_verified=True,
            date_of_birth=pending.date_of_birth,
            gender=pending.gender,
            referred_by=(
                referrer_profile.user
                if referrer_profile
                else None
            ),
        )

        MartyCoinWallet.objects.create(
            user=user
        )

        if referrer_profile:

            process_referral_reward(
                new_user=user,
                referrer_user=referrer_profile.user,
            )

        pending.delete()

        return Response(
            {
                "message":
                    "Registration completed successfully.",
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_201_CREATED,
        )