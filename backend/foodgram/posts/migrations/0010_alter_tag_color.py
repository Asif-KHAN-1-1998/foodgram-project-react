# Generated by Django 3.2.13 on 2023-11-29 22:20

import colorfield.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_alter_shoppingcard_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tag',
            name='color',
            field=colorfield.fields.ColorField(default='#FFFFFF', image_field=None, max_length=25, samples=None),
        ),
    ]