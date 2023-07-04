from rest_framework_simplejwt import authentication as jwt_authentication
from django.conf import settings
from rest_framework import authentication, exceptions as rest_exceptions
from rest_framework.request import Request


def enforce_csrf(request: Request):
    # csrf_token = request.COOKIES["XSRF-TOKEN"]
    # print(request.META["HTTP_X_CSRFTOKEN"])
    check = authentication.CSRFCheck(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise rest_exceptions.PermissionDenied('CSRF Failed: %s' % reason)


class CustomAuthentication(jwt_authentication.JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        raw_token = request.COOKIES.get(settings.SIMPLE_JWT['AUTH_COOKIE']) or None 

        if header is None:
            return None
        else:
            raw_token = self.get_raw_token(header)

        if raw_token is None:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token
