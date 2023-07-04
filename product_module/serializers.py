from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from product_module.models import Product, ProductCategory, ProductOrder, ProductImage, Wishlist


class ProductCategorySerializer(ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ('id', 'title')


class ProductSerializer(ModelSerializer):

    class Meta:
        model = Product
        fields = "__all__"
        depth = 1


class ProductImageSerializer(ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ('image',)


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = ProductOrder
        fields = "__all__"


class FavoriteSerializer(ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'
