from django.urls import path

from .views import (
    ProductListView,
    ProductDetailView,
    CustomHamperView,
    CustomHamperCalculateView
)


urlpatterns = [

    path(
        "",
        ProductListView.as_view(),
        name="product-list",
    ),

    path(
        "<int:pk>/",
        ProductDetailView.as_view(),
        name="product-detail",
    ),
    path(
        "custom-hamper/",
        CustomHamperView.as_view(),
        name="custom-hamper"
    ),
    path(
        "custom-hamper/calculate/",
        CustomHamperCalculateView.as_view(),
        name="custom-hamper-calculate"
    )
]