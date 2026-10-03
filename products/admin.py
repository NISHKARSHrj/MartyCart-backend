from django.contrib import admin

from .models import Category, Product, ProductImage, Wishlist
# Register your models here.

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {
        "slug": ("name",)
    }

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "discount_price", "stock", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "sku")
    prepopulated_fields = {
        "slug": ("name",)
    }

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ("product", "is_primary")

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("user", "product")