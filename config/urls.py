"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerSplitView 
from products.models import Wishlist

def health_check(request):
    return JsonResponse({
        "status": "healthy",
        "message": "swagat nhi krogay humara"
    })

urlpatterns = [
    # admin
    path('admin/', admin.site.urls),

    # just health check
    path('api/health/', health_check, name='health_check'),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerSplitView.as_view(url_name="schema"), name="swagger-ui"),
    # auth
    path(
        'api/auth/',
        include('accounts.urls')
    ),

    # products
    path(
        "api/categories/",
        include("products.urls")
    ),

    path(
        "api/products/",
        include("products.product_urls")
    ),
    
    # cart
    path(
        "api/cart/",
        include("cart.urls")
    ),  

    # orders
    path(
        "api/orders/",
        include("orders.urls")
    ),
    # login
    path(
        'api/auth/login/',
        TokenObtainPairView.as_view(),
        name="token_obtain_pair"
    ),
    path(
        'api/auth/token/refresh/',
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    # payments
    path(
    "api/payments/",
    include("payments.urls")
    ),

    # Wishlist
    path(
    "api/wishlist/",
    include("products.wishlist_urls")
    ),
]
