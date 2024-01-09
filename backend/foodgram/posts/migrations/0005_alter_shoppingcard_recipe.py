# Generated by Django 3.2.13 on 2023-11-17 16:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0004_alter_shoppingcard_recipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingcard',
            name='recipe',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='posts.recipe', verbose_name='Рецепт'),
        ),
    ]