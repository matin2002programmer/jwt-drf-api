# Generated by Django 4.1.5 on 2023-02-11 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product_module', '0007_alter_productslider_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_slider',
            field=models.BooleanField(default=False, verbose_name='اسلایدر'),
        ),
        migrations.DeleteModel(
            name='ProductSlider',
        ),
    ]
