from django.urls import path
from .views import MeView, RegisterView, AddressDetailView, AddressListCreateView, ReferralListView, WalletView, SendOTPView, VerifyOTPView

urlpatterns = [
    # register user
    path(
        "register/",
        RegisterView.as_view(),
        name="register"
    ),

    # profile 
    path(
        "me/",
        MeView.as_view(),
        name="me"
    ),

    # users addresses
    path(
        "addresses/",
        AddressListCreateView.as_view(),
        name="address-list-create"
    ),
    path(
        "addresses/<int:pk>/",
        AddressDetailView.as_view(),
        name="address-detail"
    ),
    # referrals
    path(
        "referrals/",
        ReferralListView.as_view(),
        name="referrals"
    ),
    # wallet
    path(
        "wallet/",
        WalletView.as_view(),
        name="wallet"
    ),
    # otp
    path(
        "send-otp/",
        SendOTPView.as_view(),
        name="send-otp"
    ),
    path(
        "verify-otp/",
        VerifyOTPView.as_view(),
        name="verify-otp"
    )
]