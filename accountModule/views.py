from django.conf import settings
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import EmailMessage
from django.db.models import Q
from django.middleware import csrf
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import exceptions as rest_exceptions, response, decorators as rest_decorators, \
    permissions as rest_permissions, status, request
from rest_framework.response import Response
from rest_framework_simplejwt import tokens, views as jwt_views

from product_module.models import ProductOrder
from . import serializers, models
from .models import User
from .serializers import CookieTokenRefreshSerializer
from .tokens import account_activation_token


def get_user_tokens(user):
    refresh: tokens.RefreshToken = tokens.RefreshToken.for_user(user)
    return {
        "refresh_token": str(refresh),
        "access_token": str(refresh.access_token)
    }


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def loginView(request):
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]
    if username is None:
        return Response("You Should Enter a username Or email")
    elif password is None:
        return Response("You Should Enter a password")

    is_active_user: User = User.objects.filter(Q(username__iexact=username) | Q(email__iexact=username)).first()
    if is_active_user is None:
        return Response("User Not exist :(", status=status.HTTP_400_BAD_REQUEST)

    if is_active_user.is_active:
        user = authenticate(email=username, password=password)
        if user is None:
            user = authenticate(username=username, password=password)

        if user is not None:
            tokens = get_user_tokens(user)
            res: response.Response = response.Response()
            res.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE'],
                value=tokens["access_token"],
                expires=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            res.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=tokens["refresh_token"],
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            res.data = tokens
            res["X-CSRFToken"] = csrf.get_token(request)
            return res
        if "@" in username:
            raise rest_exceptions.AuthenticationFailed(
                "Email or Password is incorrect!")
        else:
            raise rest_exceptions.AuthenticationFailed(
                "Username or Password is incorrect!")
    return Response("User Is Not Activated :(", status=status.HTTP_400_BAD_REQUEST)


@rest_decorators.api_view(["POST"])
@rest_decorators.permission_classes([])
def registerView(request):
    username = request.data["username"]
    email = request.data["email"]
    if not User.objects.filter(username__iexact=username, email__iexact=email).exists():
        serializer = serializers.RegistrationSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            to_email = request.data["email"].lower()

            mail_subject = 'Activate your user account.'
            # try:
            #     current_site = request.META["HTTP_REFERER"]
            # except KeyError:
            current_site = "localhost:8000"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            activation_url = reverse('accountModule:activate', kwargs={'uidb64': uid, 'token': token})
            activation_url = 'http://' + current_site + activation_url

            message = render_to_string('accountModule/template_activate_account.html', {
                'user': user,
                'domain': current_site,
                'activation_url': activation_url,
                # 'protocol': 'https' if request.is_secure() else 'http' => if in pure django
            })
            user.email_active_code = activation_url
            user.save()
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.content_subtype = 'html'
            if email.send():
                return Response("Email activation link is successfully sent, "
                                "Please confirm your email !", status=status.HTTP_200_OK)
            else:
                return Response("An internal server error tp send email occurred :(",
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    return Response("This username or email Already in use !", status=status.HTTP_400_BAD_REQUEST)


@rest_decorators.api_view(["POST", "GET"])
def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        return Response('Thank you for your email confirmation. Now you can login to your account.',
                        status=status.HTTP_200_OK)
    else:
        return Response('Activation link is invalid !', status=status.HTTP_400_BAD_REQUEST)


@rest_decorators.api_view(['POST'])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def logoutView(request):
    try:
        refreshToken = request.COOKIES.get(
            settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        token: tokens.RefreshToken = tokens.RefreshToken(refreshToken)
        token.blacklist()

        res = response.Response()
        res.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE'])
        res.delete_cookie(settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'])
        res.delete_cookie("X-CSRFToken")
        res.delete_cookie("csrftoken")
        res["X-CSRFToken"] = None

        return res
    except Exception as err:
        print(err)
        raise rest_exceptions.ParseError("Invalid token")

class CookieTokenRefreshView(jwt_views.TokenRefreshView):
    serializer_class = CookieTokenRefreshSerializer

    def finalize_response(self, request, response, *args, **kwargs):
        if response.data.get("refresh"):
            print("Yes")
            response.set_cookie(
                key=settings.SIMPLE_JWT['AUTH_COOKIE_REFRESH'],
                value=response.data['refresh'],
                expires=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                httponly=settings.SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                samesite=settings.SIMPLE_JWT['AUTH_COOKIE_SAMESITE']
            )

            del response.data["refresh"]
        response["X-CSRFToken"] = request.COOKIES.get("csrftoken")
        return super().finalize_response(request, response, *args, **kwargs)


@rest_decorators.api_view(['POST'])
def forgot_password(request):
    email = request.data.get('email')
    serializer = serializers.ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # try:
        user = User.objects.get(email=email)
        # except User.DoesNotExist:
        #     return Response({'message': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        current_site = "localhost:8000"
        mail_subject = f'Rest Password at {current_site}'
        rest_link = user.email_active_code
        rest_url = rest_link.replace('activate', 'reset-password')
        message = render_to_string('accountModule/template_rest_password_account.html', {
            'user': user,
            'domain': current_site,
            'rest_password_url': rest_url,
        })
        email = EmailMessage(mail_subject, message, to=[email])
        email.content_subtype = 'html'
        if email.send():
            return Response({'message': 'Password reset link has been sent to your email.'}, status=status.HTTP_200_OK)
        else:
            return Response("An internal server error tp send email occurred :(",
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response({'message': 'User with this email does not exist.'}, status=status.HTTP_400_BAD_REQUEST)


@rest_decorators.api_view(['POST', 'GET'])
def reset_password(request: request, uidb64, token):
    if request.method == "GET":
        current_url = request.build_absolute_uri()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user and (user.email_active_code[45:] == current_url[45:]):
            response = redirect('http://localhost:3000/auth/login/reset-password')
            response.set_signed_cookie('redirected', current_url, salt='myapp')
            return response

        if user is None or (user.email_active_code[39:] != current_url[45:]):
            return Response({'message': 'Password reset link is invalid or has expired.'},
                            status=status.HTTP_400_BAD_REQUEST)

        response = redirect('http://localhost:3000/auth/login/reset-password')
        response.set_signed_cookie('redirected', current_url, salt='myapp')
        return response

    if request.method == "POST":

        current_url = request.build_absolute_uri()

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if not user.is_active:
            user.is_active = True

        if user is not None or user.email_active_code != current_url:

            password = request.data.get('password')
            confirm_password = request.data.get('confirm_password')
            if password != confirm_password:
                return Response({'message': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

            current_site = "localhost:8000"
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = account_activation_token.make_token(user)
            reset_activation_url = reverse('accountModule:reset_password', kwargs={'uidb64': uid, 'token': token})
            rest_password_link = 'http://' + current_site + reset_activation_url

            user.email_active_code = rest_password_link

            user.set_password(password)
            user.save()

            # return redirect('http://localhost:3000/auth/login', message='Your password has been reset successfully.')
            return Response({'message': 'Your password has been reset successfully.'}, status=status.HTTP_200_OK)

        return Response({"message": "Something Are Wrong"}, status=status.HTTP_400_BAD_REQUEST)


@rest_decorators.api_view(["GET"])
@rest_decorators.permission_classes([rest_permissions.IsAuthenticated])
def user(request):
    try:
        user = models.User.objects.get(id=request.user.id)
        user_orders = ProductOrder.objects.filter(user=user)
        products = []
        for order in user_orders:
            products.append({
                "id": order.product.id,
                "user_order": order.id,
                "title": order.product.title,
                "price": order.product.price,
                "image": order.product.image.url,
                "short_description": order.product.short_description,
            })
        user_data = serializers.AccountSerializer(user).data
        response_data = {
            "user": user_data,
            "orders": products
        }
        return response.Response(response_data)
    except models.User.DoesNotExist:
        return response.Response(status=404)
