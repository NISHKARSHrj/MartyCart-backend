from django.urls import path
from .views import MeView, RegisterView, AddressDetailView, AddressListCreateView, ReferralListView, VerifyRegistrationOTPView, WalletView

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
        "verify-registration-otp/",
        VerifyRegistrationOTPView.as_view(),
        name="verify-registration-otp",
),
]