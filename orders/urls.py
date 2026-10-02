from django.urls import path

from .views import (
    OrderListCreateView,
    OrderDetailView,
    OrderStatusUpdateView,
    OrderCancelView
)


urlpatterns = [

    path(
        "",
        OrderListCreateView.as_view(),
        name="order-list-create",
    ),

    path(
        "<int:pk>/",
        OrderDetailView.as_view(),
        name="order-detail",
    ),
    path(
        "<int:pk>/status/",
        OrderStatusUpdateView.as_view(),
        name="order-status-update"
    ),
    path(
        "<int:pk>/cancel/",
        OrderCancelView.as_view(),
        name="order-cancel",
    ),
]