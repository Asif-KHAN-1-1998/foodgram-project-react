import django_filters
from django.contrib.auth import get_user_model
from django_filters import rest_framework as filters
from django_filters.rest_framework import FilterSet
from recipes.models import Ingredient, Recipe, Tag

User = get_user_model()


class TagFilter(filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Tag
        fields = ["name", "slug"]


class IngredientFilter(filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Ingredient
        fields = ["name", "measurement_unit"]


class RecipesFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name="tags__slug",
        to_field_name="slug",
    )
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all(),
    )
    is_favorited = filters.BooleanFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.BooleanFilter(
        method="get_is_in_shopping_cart",
    )

    class Meta:
        model = Recipe
        fields = ["is_favorited", "author", "tags", "is_in_shopping_cart"]

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(carts__user=user)
        return queryset
