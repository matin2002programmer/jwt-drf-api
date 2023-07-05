from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.static import serve
from django.conf import settings
from django.shortcuts import redirect

def page_not_found_view(request, exception):
    redirect('https://www.instagram.com/matindevilish_boy/')

urlpatterns = [
    path('', lambda request: redirect('https://www.instagram.com/matindevilish_boy/')),
    path('admin/', admin.site.urls),
    path('api/auth/', include("accountModule.urls", namespace='accountModule')),
    path('products/', include("product_module.urls")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
handler404 = "core.urls.page_not_found_view"
