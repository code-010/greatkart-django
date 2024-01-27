from django.contrib import admin
from .models import Product, ProductVariation

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'category', 'stock', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    
class ProductVariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'variation_category', 'variation_value', 'is_active','modified_date')
    list_editable = ('is_active',)
    list_filter = ('product', 'variation_category', 'variation_value', 'is_active',)

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariation, ProductVariationAdmin)