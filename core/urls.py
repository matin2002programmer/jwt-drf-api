from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.conf import settings
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('https://www.instagram.com/matindevilish_boy/')),
    path('admin/', admin.site.urls),
    path('api/auth/', include("accountModule.urls", namespace='accountModule')),
    path('products/', include("product_module.urls")),
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT})
] 
