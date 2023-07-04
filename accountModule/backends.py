from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .models import User


class EmailOrUsernameModelBackend(ModelBackend):
    """
    This is a ModelBacked that allows authentication
    with either a username or an email address.

    """
    def authenticate(self, request, username=None, password=None, email=None, **kwargs):

        if username:
            kwargs = {'username': username}
        else:
            kwargs = {'email': email}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None