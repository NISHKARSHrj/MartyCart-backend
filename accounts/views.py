from django.shortcuts import render
from django.contrib.auth.models import User

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Address, MartyCoinWallet
from .serializers import RegisterSerializer, AddressSerializer, UserSerializer, ReferredUserSerializer, MartyCoinWalletSerializer, SendOTPSerializer, VerifyOTPSerializer
from .services import create_phone_otp, verify_phone_otp
# Create your views here.


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

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

class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = SendOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone = serializer.validated_data["phone"]

        try:
            otp = create_phone_otp(phone)
        except ValueError as e:
            return Response({"error": str(e)}, status=400)

        # TEMPORARY:
        # WhatsApp integration ke baad
        # ye OTP response mein nahi bhejna hai.
        return Response(
            {
                "message": "OTP sent successfully.",
                "otp": otp
            },
            status=200
        )

class VerifyOTPView(APIView):

    permission_classes = [AllowAny]

    def post(self, request):

        serializer = VerifyOTPSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        phone =  serializer.validated_data["phone"]
        otp = serializer.validated_data["otp"]

        success, message = verify_phone_otp(phone, otp)

        if not success:
            return Response({
                "error": message
            }, status=400)

        return Response(
            {
                "message": "OTP verified successfully.",
                "phone": phone
            }, status=200
        )