from django.urls import path

from product_module.views import product_view, OrderView, ProductImageView, AddFavoriteView, CheckFavoritesView

urlpatterns = [
    path("", product_view, name="product_view"),
    path("add-product", OrderView.as_view(), name="order_product"),
    path('add-favorite', AddFavoriteView.as_view(), name='add_favorite'),
    path('delete-product/<int:product_id>/', OrderView.as_view(), name='delete-product'),
    path('favorite/<int:product_id>/remove-favorite', AddFavoriteView.as_view(), name='remove_favorite'),
    path('check-favorites/', CheckFavoritesView.as_view(), name='check_favorite'),
    path('product/<int:product_id>/images/', ProductImageView.as_view()),
]
