from django.urls import path
from .views import loginView, registerView, CookieTokenRefreshView, logoutView, user, activate, forgot_password, reset_password

app_name = "accountModule"

urlpatterns = [
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('reset-password/<uidb64>/<token>', reset_password, name='reset_password'),
    path('login', loginView),
    path('register', registerView),
    path('refresh-token', CookieTokenRefreshView.as_view()),
    path('logout', logoutView),
    path('forgot-password', forgot_password),
    path("user", user)
]
