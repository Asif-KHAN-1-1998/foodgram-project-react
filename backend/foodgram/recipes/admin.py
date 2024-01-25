from django.contrib import admin

from .models import (Ingredient, Recipe, Tag,
                     IngredientsInRecipe, Favourite, ShoppingCart, Subscription)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'author',
        'name',
        'image',
        'text',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'measurement_unit',)
    search_fields = ('^name',)


admin.site.register(Favourite)
admin.site.register(IngredientsInRecipe)
admin.site.register(ShoppingCart)
admin.site.register(Subscription)
admin.site.register(Tag)
