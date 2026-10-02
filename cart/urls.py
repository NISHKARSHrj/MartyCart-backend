from django.urls import path

from .views import CartView, CartItemCreateView, CartItemDeleteView, CartItemUpdateView, AddCustomHamperToCartView

urlpatterns = [
    path(
        "",
        CartView.as_view(),
        name="cart"
    ),

    path(
        "item/",
        CartItemCreateView.as_view(),
        name="cart-item-create"
    ),
    path(
        "item/<int:pk>/",
        CartItemUpdateView.as_view(),
        name="cart-item-update"
    ),
    path(
        "item/<int:pk>/",
        CartItemDeleteView.as_view(),
        name="cart-item-delete"
    ),
    path(
        "custom-hamper/",
        AddCustomHamperToCartView.as_view(),
        name="add-custom-hamper-to-cart"
    ),
]