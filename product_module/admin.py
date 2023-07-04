from django.contrib import admin
from product_module import models


class ProductAdmin(admin.ModelAdmin):
    list_filter = ['category', 'is_active']
    list_display = ['title', 'price', 'is_active', 'is_delete']
    list_editable = ['price', 'is_active']


admin.site.register(models.Product, ProductAdmin)
admin.site.register(models.ProductCategory)
admin.site.register(models.ProductTag)
admin.site.register(models.ProductBrand)
admin.site.register(models.Wishlist)
admin.site.register(models.ProductOrder)
admin.site.register(models.ProductComment)
admin.site.register(models.ProductImage)
admin.site.register(models.Color)
