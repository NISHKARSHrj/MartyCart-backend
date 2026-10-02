from django.urls import path

from .views import CategoryDetailedView, CategoryListView , CategoryProductsView


urlpatterns = [
    path(
        "",
        CategoryListView.as_view(),
        name="category-list"
    ),
    path(
        "<int:pk>/",
        CategoryDetailedView.as_view(),
        name="category-detail"
    ),
    path(
        "<int:category_id>/products/",
        CategoryProductsView.as_view(),
        name="category-products"
    ),
    
]       