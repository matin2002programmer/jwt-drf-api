# Generated by Django 4.1.5 on 2023-03-30 13:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product_module', '0016_color_remove_product_color_product_color'),
    ]

    operations = [
        migrations.RenameField(
            model_name='color',
            old_name='color',
            new_name='name',
        ),
    ]
