from django.core.exceptions import ValidationError
from django.db import models

from accountModule.models import User


class ProductCategory(models.Model):
    title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    url_title = models.CharField(max_length=300, db_index=True, verbose_name='عنوان در url')
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'دسته بندی'
        verbose_name_plural = 'دسته بندی ها'


class ProductBrand(models.Model):
    title = models.CharField(max_length=300, verbose_name='نام برند', db_index=True)
    is_active = models.BooleanField(verbose_name='فعال / غیرفعال')

    class Meta:
        verbose_name = 'برند'
        verbose_name_plural = 'برند ها'

    def __str__(self):
        return self.title


class Color(models.Model):
    name = models.CharField(max_length=20, verbose_name="رنگ محصول")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'رنگ'
        verbose_name_plural = 'رنگ محصول'


class Product(models.Model):

    title = models.CharField(max_length=300, verbose_name='نام محصول')
    category = models.ManyToManyField(ProductCategory, related_name='product_categories', verbose_name='دسته بندی ها')
    image = models.ImageField( null=True, blank=True, verbose_name='تصویر محصول')
    brand = models.ForeignKey(ProductBrand, on_delete=models.CASCADE, verbose_name='برند', null=True, blank=True)
    price = models.IntegerField(verbose_name='قیمت')
    short_description = models.CharField(max_length=360, db_index=True, null=True, verbose_name='توضیحات کوتاه')
    description = models.TextField(verbose_name='توضیحات اصلی', db_index=True)
    color = models.ManyToManyField(Color, related_name="product_color", verbose_name="رنگ محصول", blank=True)
    amount = models.IntegerField(verbose_name="تعداد محصول")
    is_active = models.BooleanField(default=False, verbose_name='فعال / غیرفعال')
    is_delete = models.BooleanField(verbose_name='حذف شده / نشده')
    is_slider = models.BooleanField(default=False, verbose_name="اسلایدر")

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.price})"

    class Meta:
        verbose_name = 'محصول'
        verbose_name_plural = 'محصولات'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images')

    def __str__(self):
        return self.product.title + "  " + self.image.url

    class Meta:
        verbose_name = 'عکس محصول'
        verbose_name_plural = 'گالری عکس محصول'


class ProductComment(models.Model):
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000, verbose_name="کامنت")

    class Meta:
        verbose_name = 'کامنت'
        verbose_name_plural = 'کامنت ها'


class ProductTag(models.Model):
    caption = models.CharField(max_length=300, db_index=True, verbose_name='عنوان')
    product = models.ManyToManyField(Product, related_name='product_tags')

    class Meta:
        verbose_name = 'تگ محصول'
        verbose_name_plural = 'تگ های محصولات'

    def __str__(self):
        return self.caption


class ProductOrder(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    quantity = models.IntegerField(verbose_name="تعداد محصول")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    color = models.CharField(max_length=21, verbose_name="رنگ محصول", default="None")

    class Meta:
        verbose_name = 'سفارشات مشتری'
        verbose_name_plural = 'سفارشات مشتری ها'

    def __str__(self):
        return str(self.user) + '  |   ' + str(self.product)

    def save(self, *args, **kwargs):
        if int(self.quantity) > int(self.product.amount):
            ValidationError("You can't order more than amount")
        else:
            super(ProductOrder, self).save(*args, **kwargs)
        

class Wishlist(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='کاربر')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='محصول')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    class Meta:
        verbose_name = 'علاقه مندی ها'
        verbose_name_plural = 'لیست علاقمندی ها'
        unique_together = ('user', 'product')

    def __str__(self):
        return str(self.user) + '  |   ' + str(self.product)
