from django.db import IntegrityError
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from product_module.models import Product, ProductOrder, ProductImage, Wishlist
from product_module.serializers import ProductSerializer, ProductImageSerializer, \
    FavoriteSerializer


# @permission_classes([permissions.IsAuthenticated])
@api_view(["GET", "POST", "DELETE", "PUT"])
def product_view(request):
    products_module = Product.objects.all()
    serializer = ProductSerializer(products_module, many=True)
    
    return Response(serializer.data, status=status.HTTP_200_OK)

    # Get the client's IP address from the request's META dictionary
    #client_ip = request.META.get('REMOTE_ADDR')

    # Add the IP address to the serialized data
    #serialized_data = serializer.data
    #serialized_data = {'data': serialized_data, 'client_ip': client_ip}

    


class OrderView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = ProductOrder.objects.filter(user=user)
        products = {}
        for order in orders:
            products["id"] = order.product.id
            products["name"] = order.product.name
        return Response(products)

    def post(self, request):
        user = request.user
        product_id = request.data.get('id')
        product = Product.objects.get(id=product_id)
        user_order: ProductOrder = ProductOrder.objects.filter(user=user)
        for order in user_order:
            if order.product.id == product_id:
                if int(request.data["quantity"] + order.quantity) > int(product.amount):
                    return Response({"status": "Can't order more than stock"}, status=status.HTTP_406_NOT_ACCEPTABLE)

                increase_quantity = int(order.quantity) + int(request.data["quantity"])
                order.quantity = increase_quantity
                order.save()
                return Response({"status": "Add Successfully"}, status=status.HTTP_200_OK)
        if int(request.data["quantity"]) > int(product.amount):
            return Response({"status": "Can't order more than stock"}, status=status.HTTP_406_NOT_ACCEPTABLE)

        ProductOrder.objects.create(
            user=user,
            product=product,
            quantity=request.data.get("quantity"),
            color=request.data.get("color")
        )
        return Response({'status': 'Order created'}, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        user = request.user
        try:
            order = ProductOrder.objects.filter(id=product_id, user=user)
            if order is None:
                return Response({"status": "Order not found"}, status=status.HTTP_404_NOT_FOUND)
        except ProductOrder.DoesNotExist:
            return Response({"status": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        order.delete()
        return Response({"status": "Order deleted"}, status=status.HTTP_200_OK)


class ProductImageView(APIView):
    def get(self, request, product_id):
        images = ProductImage.objects.filter(product=product_id)
        serializer = ProductImageSerializer(images, many=True)
        return Response(serializer.data)


class AddFavoriteView(APIView):
    authentication_classes = [JWTAuthentication]

    def post(self, request):
        user = request.user
        product = Product.objects.get(id=request.data["product_id"])
        try:
            favorite = Wishlist.objects.create(user=user, product=product)
        except IntegrityError:
            return Response({'error': 'Favorite already exists.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, product_id):
        user = request.user
        product = Product.objects.get(id=product_id)

        try:
            favorite = Wishlist.objects.get(user=user, product=product)
        except Wishlist.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)

        favorite.delete()
        return Response({"success": "product was deleted from user favorite"}, status=status.HTTP_200_OK)


class CheckFavoritesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        user = request.user
        product_ids = request.data.get('product_ids', [])
        favorites = {}

        for product_id in product_ids:
            is_already_favorite = Wishlist.objects.filter(user=user, product_id=product_id).exists()
            favorites[product_id] = is_already_favorite

        return Response(favorites, status=status.HTTP_200_OK)
