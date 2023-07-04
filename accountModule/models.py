from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password=None, **kwargs):

        if not email:
            raise ValueError("Email is required")

        if not username:
            raise ValueError("Username is required")

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, username, password, **kwargs):
        user = self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return


class User(AbstractUser):
    avatar = models.ImageField(verbose_name='عکس پروفایل', null=True, blank=True, upload_to='Avatars')
    first_name = models.CharField(max_length=30, verbose_name='نام')
    last_name = models.CharField(max_length=30, verbose_name='نام خانوادگی')
    phone_number = models.CharField(max_length=11, verbose_name='شماره',null=True,blank=True)
    email_active_code = models.CharField(max_length=280, verbose_name='کد فعالسازی ایمیل')
    address = models.TextField(verbose_name='آدرس', blank=True)
    postal_code = models.CharField(max_length=30, verbose_name='کد پستی', blank=True)
    city_residence = models.CharField(max_length=30, verbose_name='شهر محل زندگی', blank=True)

    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        if self.get_full_name():
            return self.get_full_name()
        else:
            return self.username
