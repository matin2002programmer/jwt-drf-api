from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings

urlpatterns = [
    path('', lambda request: redirect('https://www.instagram.com/matindevilish_boy/')),
    path('admin/', admin.site.urls),
    path('api/auth/', include("accountModule.urls", namespace='accountModule')),
    path('products/', include("product_module.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
